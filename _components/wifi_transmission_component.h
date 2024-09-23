#ifndef WIFI_TRANSMISSION_COMPONENT
#define WIFI_TRANSMISSION_COMPONENT

#include "esp_netif.h"
#include "esp_log.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>

#include <string>

#ifndef CONFIG_DEST_IP_ADDR
    #define CONFIG_DEST_IP_ADDR "192.168.4.3"
#endif

#ifndef CONFIG_DEST_UDP_PORT
    #define CONFIG_DEST_UDP_PORT 5000
#endif


void transmit_data(const std::string& str) {
    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(CONFIG_DEST_IP_ADDR);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(CONFIG_DEST_UDP_PORT);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if(sock < 0) {
        ESP_LOGE("E", "Unable to create socket: errno %d", errno);
        return;
    }

    int cerr = connect(sock, (const struct sockaddr *) &dest_addr, sizeof(dest_addr));
    if(cerr < 0) {
        ESP_LOGE("E", "Error during connect: errno %d", errno);
    }

    int err = 0;
    do {
        err = sendto(sock, str.c_str(), str.size(), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if(err < 0) {
            ESP_LOGE("E", "Error occurred during sending: errno %d", errno);
            break;
        }
        vTaskDelay(1);
    } while(err != str.size());

    shutdown(sock, SHUT_RDWR);
    close(sock);
}

#endif //WIFI_TRANSMISSION_COMPONENT
