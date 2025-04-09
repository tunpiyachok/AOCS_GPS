//AOCS_Shell
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>
#include <mqueue.h>
#include <sys/stat.h>
#include <string.h>
#include <stdint.h>
#include <sys/resource.h>
#include <time.h>
#include "message.h"

Message struct_type = {0}; // Initialize to 0
Message send_msg = {0}; // Initialize to 0
Message receive_msg = {0}; // Initialize to 0

void tcc_type(void*arg) //recive from flight software and send to AOCS system
{
    mqd_t mq_GPS = mq_open("/mq_GPS", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes); //send to TM_Monitor
    if (mq_GPS == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }
    mqd_t mq_tc_gps = mq_open("/mq_tc_gps", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes); //send to TC_Monitor
    if (mq_tc_gps == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }

    // ??????????? message queue ???????????????????????? msg_dis_can
    mqd_t mqdes_type = mq_open("/mq_dispatch", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes); // receive from flight software
    if (mqdes_type == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }

    while(1) {
        if (mq_receive(mqdes_type, (char *)&receive_msg, sizeof(Message), NULL) == -1) {
            perror("mq_receive");
            exit(EXIT_FAILURE);
        }

        printf("Receive Type : %hhu\n", receive_msg.type);

        if (receive_msg.type == 0 && receive_msg.mdid == 3) {
            send_msg = receive_msg;
            printf("Send Module ID : %hhu\n", send_msg.mdid);
            printf("Send Request ID : %hhu\n", send_msg.req_id);
            if (mq_send(mq_GPS, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                perror("mq_send");
                exit(EXIT_FAILURE);
            }
            printf("\n-- Wait for respond --\n");
        } else if(receive_msg.type == 2 && receive_msg.mdid == 3) {
            send_msg = receive_msg;
            printf("Send Module ID : %hhu\n", send_msg.mdid);
            printf("Send Request ID : %hhu\n", send_msg.req_id);
            printf("Send Parameter : %hhu\n", send_msg.param);
            if (mq_send(mq_tc_gps, (char *)&send_msg, sizeof(Message), 1) == -1) {
                perror("mq_send");
                exit(EXIT_FAILURE);
            }
            printf("-------------------------------------------\n");
        } 
        send_msg = (Message){0};
        receive_msg = (Message){0};
    }

    mq_close(mqdes_type);
    mq_close(mq_GPS);
    mq_close(mq_tc_gps);
    mq_unlink("/mq_tc_gps");
    mq_unlink("/mq_GPS");
    mq_unlink("/mq_dispatch");
}

void request_return(void*arg) //recive from AOCS system and return to flight software
{
	mqd_t mq_receive_req = mq_open("/mq_receive_req", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes); //return from AOCS system
	if (mq_receive_req == -1) 
	{
		perror("mq_open");
		exit(EXIT_FAILURE);
	}
	
	mqd_t mq_return = mq_open("/mq_dispatch", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes); //return to sender
	if (mq_return == -1) 
	{
		perror("mq_open");
		exit(EXIT_FAILURE);
	}
	while(1)
	{
		Message send_msg = {0};
		Message receive_msg = {0};
		if (mq_receive(mq_receive_req, (char *)&receive_msg, sizeof(Message), NULL) == -1) 
		{
			perror("mq_receive");
			exit(EXIT_FAILURE);
		}
		send_msg = receive_msg;
		printf("Receive Type : %hhu\n", receive_msg.type);
		printf("Module ID : %u\n", send_msg.mdid);
		if(receive_msg.type == 1)
		{
		    printf("Telemetry ID : %u\n", send_msg.req_id);
			send_msg.val;
		}
		else if(receive_msg.type == 3)
		{
			printf("Telecommand ID : %hhu\n", send_msg.req_id); 
		    send_msg.type = 3;
		    printf("Parameter : %hhu\n", send_msg.param);
			send_msg.val;
		}
		
		else
		{
			printf("Have no Type\n");
			send_msg.type;
			printf("Module ID : %u\n", send_msg.mdid);
			send_msg.req_id = 0;
			printf("-------------------------------------------\n\n");
		}
		
		if (mq_send(mq_return, (char *)&send_msg, sizeof(Message), 1) == -1) 
		{
			perror("mq_send");
			exit(EXIT_FAILURE);
		}
		printf("-------------------------------------------\n\n");
		
	}
	mq_close(mq_receive_req);
		mq_close(mq_return);
		mq_unlink("/mq_dispatch");
		mq_unlink("/mq_receive_req");

	
}


int main()
{
	pthread_t type, send;
	
	pthread_create(&type, NULL, (void *(*)(void *))tcc_type, NULL);
	pthread_create(&send, NULL, (void *(*)(void *))request_return, NULL);

	
	pthread_join(type, NULL);
	pthread_join(send, NULL);
}
