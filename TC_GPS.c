/*
Development by : Piyachok Ridsadaeng
*/
//Telecommand GPS monitoring
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <time.h>
#include <mqueue.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include "message.h"
#include "gps.h"
#include <pthread.h>

Message receive_msg = {0};
Message send_msg = {0};

// receive from AOCS shell and send command to GPS module
void send(void*arg)
{
    struct mq_attr attributes = {
    	    .mq_flags = 0,
    	    .mq_maxmsg = 10,
    	    .mq_curmsgs = 0,
    	    .mq_msgsize = sizeof(Message)
    	  };
    mqd_t mq_telecommand = mq_open("/mq_tc_gps", O_CREAT | O_RDWR, S_IRWXU, &attributes);// receive from AOCS shell
    if (mq_telecommand == -1)
    {
        perror("mq_open()");
        exit(1);
    }
    mqd_t mq_send_read = mq_open("/mq_telecommand_send_read", O_CREAT | O_RDWR, S_IRWXU, &attributes);// send to GPS module for sampling value
    if (mq_send_read == -1)
    {
        perror("mq_open()");
        exit(1);
    }
    mqd_t mq_send_log = mq_open("/mq_telecommand_send_log", O_CREAT | O_RDWR, S_IRWXU, &attributes);// send to GPS module for log value
    if (mq_send_log == -1)
    {
        perror("mq_open()");
        exit(1);
    }
    mqd_t mqdes_send = mq_open("/mq_receive_req", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);// return to AOCS shell
    if (mqdes_send == -1) {
        perror("mq_open /mq_receive_req");
        exit(EXIT_FAILURE);
    }

    while (1)
    {
        if (mq_receive(mq_telecommand, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1)// receive message from AOCS shell
        {
            perror("mq_receive()");
            exit(1);
        }

        if (receive_msg.mdid == 3 && receive_msg.req_id == 1)
        {
        	send_msg = receive_msg;
        	send_msg.val = 0;
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
          printf("---------------------With for response----------------------\n\n");
          if (mq_send(mq_send_read, (char *)&send_msg, sizeof(send_msg), 1) == -1) // send message to GPS module for start sampling
    			{
    				perror("mq_send");
    				exit(EXIT_FAILURE);
    			}  
        }
        else if (receive_msg.mdid == 3 && receive_msg.req_id == 2)
        {
        	send_msg = receive_msg;
        	send_msg.val = 1;
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
          printf("---------------------With for response----------------------\n\n");
          if (mq_send(mq_send_read, (char *)&send_msg, sizeof(send_msg), 1) == -1) // send message to GPS module for stop sampling
    			{
    				perror("mq_send");
    				exit(EXIT_FAILURE);
    			}  
        }
        else if (receive_msg.mdid == 3 && receive_msg.req_id == 3 && (receive_msg.param >= 5 && receive_msg.param <= 60))
        {
        	send_msg = receive_msg;
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	        printf("Parameter. : %hhu\n",send_msg.param);
          printf("---------------------With for response----------------------\n\n");
          if (mq_send(mq_send_log, (char *)&send_msg, sizeof(send_msg), 1) == -1)  // send message to GPS module for start log
    			{
    				perror("mq_send");
    				exit(EXIT_FAILURE);
    			}  
        }
        else if (receive_msg.mdid == 3 && receive_msg.req_id == 4)
        {
        	send_msg = receive_msg;
	        printf("Module : %hhu\n",send_msg.mdid);
	        printf("Request : %hhu\n",send_msg.req_id);
	        printf("Parameter : %hhu\n",send_msg.param);
          printf("---------------------With for response----------------------\n\n");
          if (mq_send(mq_send_log, (char *)&send_msg, sizeof(send_msg), 1) == -1) // send message to GPS module for stop log
    			{
    				perror("mq_send");
    				exit(EXIT_FAILURE);
    			}  
        }
        else
	    {
             receive_msg.type = 3;
	    	    receive_msg.param = 0;
            printf("Module : %hhu\n",receive_msg.mdid);
            printf("Request : %hhu\n",receive_msg.req_id);
            printf("Return Parameter : %u\n",receive_msg.param);
            printf("[TC_GPS] Unknown request received.\n");
            printf("-------------------------------------------\n\n");
            if (mq_send(mqdes_send, (char *)&receive_msg, sizeof(receive_msg), 1) == -1) // return message to AOCS shell
	    {
                perror("mq_send /mq_receive_req");
                exit(EXIT_FAILURE);
            }
		  }
        
        	Message send_msg = {0};
		Message receive_msg = {0};
    }
  	mq_close(mq_send_read);
     mq_close(mq_send_log);
  	mq_close(mq_telecommand);
    mq_unlink("/mq_telecommand_send_read");
    mq_unlink("/mq_telecommand_send_log");
    mq_unlink("/mq_telecommand");
    	

}

//receive from GPS module and return to AOCS shell
void return_AOCS_shell(void* arg) {
    struct mq_attr attributes = {
        .mq_flags = 0,
        .mq_maxmsg = 10,
        .mq_curmsgs = 0,
        .mq_msgsize = sizeof(Message)
    };

    mqd_t mq_return = mq_open("/mq_return", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);// receive from GPS module
    if (mq_return == -1) {
        perror("mq_open /mq_return");
        exit(EXIT_FAILURE);
    }

    mqd_t mqdes_send = mq_open("/mq_receive_req", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);// return to AOCS shell
    if (mqdes_send == -1) {
        perror("mq_open /mq_receive_req");
        exit(EXIT_FAILURE);
    }

    while (1) {
        Message receive_msg = {0};

        if (mq_receive(mq_return, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) {// receive message from GPS module
            perror("mq_receive /mq_return");
            exit(EXIT_FAILURE);
        }

        if (receive_msg.mdid == 3 && 
            (receive_msg.req_id == 1 || receive_msg.req_id == 2 || receive_msg.req_id == 3 || receive_msg.req_id == 4)) {
            printf("Module : %hhu\n",receive_msg.mdid);
            printf("Request : %hhu\n",receive_msg.req_id);
            printf("Return Parameter : %u\n",receive_msg.param);
            printf("-------------------------------------------\n\n");

            if (mq_send(mqdes_send, (char *)&receive_msg, sizeof(receive_msg), 1) == -1) {// return to AOCS shell
                perror("mq_send /mq_receive_req");
                exit(EXIT_FAILURE);
            }
        }
    }

    mq_close(mq_return);
    mq_close(mqdes_send);
    mq_unlink("/mq_return");
    mq_unlink("/mq_receive_req");
}



int main()
{
	pthread_t send_gps, return_shell;
	
	pthread_create(&send_gps, NULL, (void *(*)(void *))send, NULL);
	pthread_create(&return_shell, NULL, (void *(*)(void *))return_AOCS_shell, NULL);

	
	pthread_join(send_gps, NULL);
	pthread_join(return_shell, NULL);
 
 	mq_unlink("/mq_AOCS_Shell");
	mq_unlink("/mq_telecommand_send_read");
	mq_unlink("/mq_telecommand");
	mq_unlink("/mq_telecommand_send_log");
    
}
