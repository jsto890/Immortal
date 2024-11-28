#include <iostream>
#include <string>
#include <thread>
#include <windows.h>
#include <endpointvolume.h>
#include <mmdeviceapi.h>
#include <opencv2/opencv.hpp>
#include "StreamDeckSDK.h"

bool is_muted = false;
std::string ASSETS_PATH = "Assets/";

void render_key_image(StreamDeckSDK::StreamDeck& deck, int key, const std::string& icon_filename, const std::string& label_text) {
    cv::Mat icon = cv::imread(ASSETS_PATH + icon_filename);
    cv::resize(icon, icon, cv::Size(deck.getKeyWidth(), deck.getKeyHeight()));
    cv::putText(icon, label_text, cv::Point(icon.cols / 2, icon.rows - 5), cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(255, 255, 255), 1, cv::LINE_AA);
    deck.setKeyImage(key, icon);
}

void update_key_image(StreamDeckSDK::StreamDeck& deck, int key, bool state) {
    std::string icon = (key == 1 && is_muted) ? "mute.png" : "volume.png";
    std::string label = (key == 1 && is_muted) ? "Muted" : "Unmuted";
    render_key_image(deck, key, icon, label);
}

void set_touchscreen_image(StreamDeckSDK::StreamDeck& deck, const std::string& image_path) {
    cv::Mat image = cv::imread(ASSETS_PATH + image_path);
    cv::resize(image, image, cv::Size(800, 100));
    deck.setTouchscreenImage(image);
}

void update_touchscreen_image(StreamDeckSDK::StreamDeck& deck) {
    std::string image_path = is_muted ? "mute.png" : "volume.png";
    set_touchscreen_image(deck, image_path);
}

void toggle_mute() {
    CoInitialize(nullptr);
    IMMDeviceEnumerator* deviceEnumerator = nullptr;
    CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&deviceEnumerator));
    IMMDevice* defaultDevice = nullptr;
    deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &defaultDevice);
    IAudioEndpointVolume* endpointVolume = nullptr;
    defaultDevice->Activate(__uuidof(IAudioEndpointVolume), CLSCTX_INPROC_SERVER, nullptr, (void**)&endpointVolume);
    is_muted = !is_muted;
    endpointVolume->SetMute(is_muted, nullptr);
    endpointVolume->Release();
    defaultDevice->Release();
    deviceEnumerator->Release();
    CoUninitialize();
}

void key_change_callback(StreamDeckSDK::StreamDeck& deck, int key, bool state) {
    std::cout << "Deck Key " << key << " = " << state << std::endl;
    if (key >= deck.getKeyCount()) return;
    update_key_image(deck, key, state);
    if (state) {
        if (key == 0) {
            system("start https://www.google.com");
        } else if (key == 1) {
            toggle_mute();
            update_key_image(deck, key, state);
            update_touchscreen_image(deck);
        }
    }
}

void touchscreen_event_callback(StreamDeckSDK::StreamDeck& deck, int event, int value) {
    if (event == StreamDeckSDK::TouchscreenEventType::SHORT) {
        toggle_mute();
        update_touchscreen_image(deck);
        update_key_image(deck, 1, true);
    }
}

void dial_change_callback(StreamDeckSDK::StreamDeck& deck, int dial, int event, int value) {
    if (event == StreamDeckSDK::DialEventType::TURN) {
        std::cout << "Dial " << dial << " turned: " << value << std::endl;
        if (dial == 1) {
            CoInitialize(nullptr);
            IMMDeviceEnumerator* deviceEnumerator = nullptr;
            CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&deviceEnumerator));
            IMMDevice* defaultDevice = nullptr;
            deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &defaultDevice);
            IAudioEndpointVolume* endpointVolume = nullptr;
            defaultDevice->Activate(__uuidof(IAudioEndpointVolume), CLSCTX_INPROC_SERVER, nullptr, (void**)&endpointVolume);
            float currentVolume = 0.0f;
            endpointVolume->GetMasterVolumeLevelScalar(&currentVolume);
            float newVolume = std::max(0.0f, std::min(1.0f, currentVolume + value * 0.01f));
            endpointVolume->SetMasterVolumeLevelScalar(newVolume, nullptr);
            std::cout << "Volume set to: " << newVolume * 100.0f << "%" << std::endl;
            endpointVolume->Release();
            defaultDevice->Release();
            deviceEnumerator->Release();
            CoUninitialize();
        }
    } else if (event == StreamDeckSDK::DialEventType::PUSH) {
        toggle_mute();
        update_key_image(deck, 1, true);
        update_touchscreen_image(deck);
    }
}

int main() {
    StreamDeckSDK::DeviceManager deviceManager;
    auto streamdecks = deviceManager.enumerate();
    std::cout << "Found " << streamdecks.size() << " Stream Deck(s)." << std::endl;

    for (auto& deck : streamdecks) {
        if (!deck->isVisual()) continue;
        deck->open();
        deck->reset();
        std::cout << "Opened '" << deck->getDeckType() << "' device (serial number: '" << deck->getSerialNumber() << "', fw: '" << deck->getFirmwareVersion() << "')" << std::endl;
        deck->setBrightness(60);
        for (int key = 0; key < deck->getKeyCount(); ++key) {
            update_key_image(*deck, key, false);
        }
        deck->setKeyCallback(key_change_callback);
        deck->setDialCallback(dial_change_callback);
        deck->setTouchscreenCallback(touchscreen_event_callback);
        update_touchscreen_image(*deck);
    }

    std::this_thread::sleep_for(std::chrono::hours(1));
    return 0;
}