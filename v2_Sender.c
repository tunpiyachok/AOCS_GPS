//Sender
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  // for sleep(), usleep()
#include <pthread.h> // the header file for the pthread lib
#include <fcntl.h>
#include <mqueue.h>
#include <sys/stat.h>
#include <string.h>
#include <stdint.h> 
#include <sys/resource.h>
#include <ctype.h>
#include <time.h>
#include "message.h"

int is_valid_number(const char *input) {
    while (*input) {
        if (!isdigit((unsigned char)*input)) {
            return 0;
        }
        input++;
    }
    return 1;
}

void* request(void* arg) {
    mqd_t mqdes_type = mq_open("/mq_dispatch", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, NULL);
    if (mqdes_type == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }
    
    while (1) {
        Message send_msg = {0};
        char input[100];

        while (1) {
            printf("Enter Type((0) = Telemetry , (2) = Telecommand) : ");
            fgets(input, sizeof(input), stdin);
            input[strcspn(input, "\n")] = '\0';  // Remove newline character
            if (!is_valid_number(input) || sscanf(input, "%hhu", &send_msg.type) != 1) {
                printf("Invalid input. Please enter again.\n");
                printf("-------------------------------------------\n\n");
                continue;
            }
            break;
        }

        while (1) {
            printf("Enter Module ID : ");
            fgets(input, sizeof(input), stdin);
            input[strcspn(input, "\n")] = '\0';  // Remove newline character
            if (!is_valid_number(input) || sscanf(input, "%hhu", &send_msg.mdid) != 1) {
                printf("Invalid input. Please enter again.\n");
                printf("-------------------------------------------\n\n");
                continue;
            }
            break;
        }

        while (1) {
            printf("Enter Request ID : ");
            fgets(input, sizeof(input), stdin);
            input[strcspn(input, "\n")] = '\0';  // Remove newline character
            if (!is_valid_number(input) || sscanf(input, "%hhu", &send_msg.req_id) != 1) {
                printf("Invalid input. Please try again.\n");
                printf("-------------------------------------------\n\n");
                continue;
            }
            break;
        }

        if (send_msg.type == 2 && (send_msg.req_id != 1 && send_msg.req_id != 2 && send_msg.req_id != 4)) {
            while (1) {
                printf("Enter Parameter : ");
                fgets(input, sizeof(input), stdin);
                input[strcspn(input, "\n")] = '\0';  // Remove newline character
                if (!is_valid_number(input) || sscanf(input, "%hhu", &send_msg.param) != 1) {
                    printf("Invalid input. Please try again.\n");
                    printf("-------------------------------------------\n\n");
                    continue;
                }
                break;
            }
        }

        printf("-------------------------------------------\n\n");
        printf("Send Type : %hhu\n", send_msg.type);
        printf("Send Module_ID : %hhu\n", send_msg.mdid);
        printf("Send Request_ID : %hhu\n", send_msg.req_id);
        if (send_msg.type == 2) {
            printf("Send Parameter : %hhu\n", send_msg.param);
        }

        if (mq_send(mqdes_type, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
            perror("mq_send");
            exit(EXIT_FAILURE);
        }
        printf("\n-- Wait for respond --\n");
        sleep(1);
    }

    mq_close(mqdes_type);
    mq_unlink("/mq_dispatch");

    return NULL;
}

void* display(void*arg)
{
	mqd_t mq_return = mq_open("/mq_dispatch", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);
	if (mq_return == -1) 
	{
        perror("mq_open");
        exit(EXIT_FAILURE);
    }
    while(1)
    {
		Message receive_msg = {0};
		if (mq_receive(mq_return, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) {
            perror("mq_receive");
            exit(EXIT_FAILURE); 
        }
        if (receive_msg.type == 3 && receive_msg.mdid == 3 && receive_msg.req_id == 1) 
		{
	        printf("Module : %hhu\n",receive_msg.mdid);
	        printf("Request : %hhu\n",receive_msg.req_id);
	    	printf("Parameter : %u\n", receive_msg.param);
      printf("-------------------------------------------\n\n");
	    }
	    
	    else if (receive_msg.type == 3 && receive_msg.mdid == 3 && receive_msg.req_id == 2) 
		{
	        printf("Module : %hhu\n",receive_msg.mdid);
	        printf("Request : %hhu\n",receive_msg.req_id);
	    	printf("Parameter : %u\n", receive_msg.param);
                          printf("-------------------------------------------\n\n");
	    }
	    
        else if (receive_msg.type == 1 && receive_msg.mdid == 3 && receive_msg.req_id == 1) 
		{
	        printf("Module : %hhu\n",receive_msg.mdid);
	        printf("Request : %hhu\n",receive_msg.req_id);
	    	printf("Find GPS : %u\n", receive_msg.val);
                     printf("-------------------------------------------\n\n");
	    }
		if(receive_msg.type == 1 && receive_msg.mdid == 3 && receive_msg.req_id == 2)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("GPS Status : %u\n", receive_msg.val);
			printf("-------------------------------------------\n\n");
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 3 && receive_msg.req_id == 3)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("UNIXTIME : %u\n", receive_msg.val);
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 3 && receive_msg.req_id == 4)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("Latitude : %f\n", receive_msg.val*0.000001);
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 5)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("Longitude : %f\n", receive_msg.val*0.000001);
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 6)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("Altitude : %.2f\n", receive_msg.val*0.01);
			printf("-------------------------------------------\n\n");
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 7)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("Satellites Used : %u\n", receive_msg.val);
            if(receive_msg.val <= 0 || receive_msg.val >= 13)
            {
            	printf("Alert : GPS is unusual\n");
			}
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 8)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("HDOP : %.2f\n", receive_msg.val*0.01);
            if(receive_msg.val <= 0)
            {
            	printf("Alert : GPS is unusual\n");
			}
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 9)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("COGs : %u\n", receive_msg.val*0.01);
			printf("-------------------------------------------\n\n");	
		}
		else if(receive_msg.type == 1 && receive_msg.mdid == 2 && receive_msg.req_id == 10)
		{
			printf("Module ID : %hhu\n", receive_msg.mdid);
            printf("Telemetry ID : %hhu\n", receive_msg.req_id);
            printf("SOG : %.3f m/s\n", receive_msg.val*0.001);
			printf("-------------------------------------------\n\n");	
		}
		
		
	}
	mq_close(mq_return);
	mq_unlink("/mq_dispatch");
}

int main()
{
	pthread_t sender, receiver;
	
	pthread_create(&sender, NULL, &request, NULL);
	pthread_create(&receiver, NULL, &display, NULL);
	pthread_join(sender, NULL);
	pthread_join(receiver, NULL);
	
	return 0;
}
