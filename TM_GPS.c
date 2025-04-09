/*
Development by : Piyachok Ridsadaeng
*/
//Temetry GPS monitoring
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <time.h>
#include <stdlib.h>
#include <mqueue.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include "message.h"
#include "gps.h"
#include <pthread.h>

Message send_msg = {0};
Message receive_msg = {0};

/*
GPS_variable[0] = GPS status
GPS_variable[1] = find GPS
GPS_variable[2] = GPS time
GPS_variable[3] = Latitude
GPS_variable[4] = Longitude
GPS_variable[8] = Direction N/S
GPS_variable[9] = Direction E/W
*/

int main()
{	
	pthread_t GPS,update,log_thread;
	
	pthread_attr_t attr;
 
  
	
	pthread_attr_init(&attr);
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
	
  	pthread_create(&log_thread, NULL, Log, NULL);
	pthread_create(&update, &attr, &update_variable, NULL);
	pthread_create(&GPS, NULL, &read_GPS, NULL);
	
	mqd_t mq_GPS = mq_open("/mq_GPS", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);// receive from AOCS shell
	if (mq_GPS == -1) 
	{
	    perror("mq_open");
	    exit(EXIT_FAILURE);
	}
	mqd_t mqdes_send = mq_open("/mq_receive_req", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);// return to AOCS shell
	if (mqdes_send == -1) {
	    perror("mq_open");
	    exit(EXIT_FAILURE);
	}
	while (1)
	{
		Message send_msg = {0};
		Message receive_msg = {0};
		if (mq_receive(mq_GPS, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) 
		{
			perror("mq_receive");
			exit(EXIT_FAILURE);
		}
		send_msg = receive_msg;
		if (receive_msg.mdid == 3 && receive_msg.req_id == 1) 
		{
	        send_msg.val = GPS_variable[1];
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	printf("Find GPS : %u\n", send_msg.val);
	    	send_msg.type = 1;
	    	printf("-------------------------------------------\n\n");
	    }
		else if (receive_msg.mdid == 3 && receive_msg.req_id == 2) 
		{
	        send_msg.val = GPS_variable[0];
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	printf("Status : %u\n", send_msg.val);
	    	send_msg.type = 1;
	    	printf("-------------------------------------------\n\n");
	    }
	    else if (receive_msg.mdid == 3 && receive_msg.req_id == 3) 
		{
	        send_msg.val = GPS_variable[2];
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	printf("UNIXTIME : %u\n", send_msg.val);
	    	send_msg.type = 1; 
	    	printf("-------------------------------------------\n\n");
	    }
	    else if (receive_msg.mdid == 3 && receive_msg.req_id == 4) 
		{
			send_msg.val = GPS_variable[3];
			send_msg.param = GPS_variable[8];
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	printf("Latitude : %u\n", send_msg.val);
	    	send_msg.type = 1; 
	    	printf("-------------------------------------------\n\n");
	    }
	    else if (receive_msg.mdid == 3 && receive_msg.req_id == 5) 
		{
			send_msg.val = GPS_variable[4];
			send_msg.param = GPS_variable[9];
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	printf("Longitude : %u\n", send_msg.val);
	    	send_msg.type = 1; 
	    	printf("-------------------------------------------\n\n");
	    }

	    else if(receive_msg.mdid != 3)
	    {
	    	printf("Request has deny\n");
	    	printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	    	send_msg.mdid = 0;
	    	send_msg.req_id = 0;
	    	send_msg.val = 0;
	    	send_msg.type = 1; 
	    	printf("-------------------------------------------\n\n");
		}
	    if (mq_send(mqdes_send, (char *)&send_msg, sizeof(send_msg), 1) == -1) 
		{
			perror("mq_send");
			exit(EXIT_FAILURE);
		}  
	}
	mq_close(mq_GPS);
	mq_close(mqdes_send);
	mq_unlink("/mq_GPS");
	mq_unlink("/mq_receive_req"); 
	
	pthread_join(GPS, NULL);
	return 0;
}
