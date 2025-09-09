#ifndef WIFI_TRANSMISSION_COMPONENT
#define WIFI_TRANSMISSION_COMPONENT

#include "esp_netif.h"
#include "esp_log.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>

#include <memory>
#include <string_view>

#ifndef CONFIG_DEST_IP_ADDR
#define DEST_IP_ADDR "192.168.4.3"
#else
#define DEST_IP_ADDR CONFIG_DEST_IP_ADDR
#endif

#ifndef CONFIG_DEST_UDP_PORT
#define DEST_UDP_PORT 5000
#else
#define DEST_UDP_PORT CONFIG_DEST_UDP_PORT
#endif

#ifdef CONFIG_KEEP_UDP_SOCKET
#define KEEP_UDP_SOCKET 1
#define SOCKET_STATICNESS static
#else
#define KEEP_UDP_SOCKET 0
#define SOCKET_STATICNESS
#endif

SemaphoreHandle_t wifi_mutex = xSemaphoreCreateMutex();

int getSocket() {
    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(DEST_IP_ADDR);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(DEST_UDP_PORT);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if(sock < 0) {
        ESP_LOGE("E", "Unable to create socket: errno %d", errno);
        return sock;
    }

    int cerr = connect(sock, (const struct sockaddr *) &dest_addr, sizeof(dest_addr));
    if(cerr < 0) {
        ESP_LOGE("E", "Error during connect: errno %d", errno);
    }

    return sock;
}

template <typename ContainerT>
void transmit_data(const ContainerT& str) {
    xSemaphoreTake(wifi_mutex, portMAX_DELAY);

    SOCKET_STATICNESS int sock = getSocket();
    if(sock < 0) return;

    int err = 0;
    do {
        err = send(sock, str.data(), str.size(), 0);
        if(err < 0) {
            ESP_LOGE("E", "Error occurred during sending: errno %d", errno);
            break;
        }
        vTaskDelay(1);
    } while(err != str.size());

#if !KEEP_UDP_SOCKET
    shutdown(sock, SHUT_RDWR);
    close(sock);
#endif

    xSemaphoreGive(wifi_mutex);
}

#endif //WIFI_TRANSMISSION_COMPONENT
