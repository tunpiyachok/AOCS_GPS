#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <math.h>
#include <time.h>
#include <sys/resource.h>
#include <stdlib.h>
#include <mqueue.h>
#include "gps.h"
#include "message.h"
#include <pthread.h>

void *read_GPS(void *arg);
void *Log(void *arg);
void *update_variable(void* arg);
int checksum_valid(char *string);
int parse_comma_delimited_str(char *string, char **fields, int max_fields);
int OpenGPSPort(const char *devname);

char NMEA[MAX_FIELDS][255] = {0};
int GPS_variable[20] = {0};

void status()
{   
    if (NMEA[0][0] == 'A') 
    {
        NMEA[0][0] = '1';
    } 
    if (NMEA[0][0] == 'V') 
    {
        NMEA[0][0] = '0';
    }
    if (NMEA[0][0] == '\0') 
    {
        NMEA[0][0] = '0'; // ???????????? '0' ????????????????????????? \0
    }
    
    GPS_variable[0] = NMEA[0][0] - '0';
}


int days_between(struct tm start_date, struct tm end_date) {
    time_t start = mktime(&start_date);
    time_t end = mktime(&end_date);

    double difference = difftime(end, start) / (60 * 60 * 24);
    return (int)difference;
}

void GPS_time()
{
	char UTC_str[10];
	char DATE_str[10];
	
    strcpy(UTC_str, NMEA[1]);
    strcpy(DATE_str, NMEA[2]);

    int UTC = atoi(UTC_str);
    int DATE = atoi(DATE_str);
	
	int hour = (UTC/10000)*3600;
	int min = ((UTC%10000)/100)*60;
	int sec = (UTC%100);
	
	int day = (DATE/10000);
	int month = (DATE%10000)/100;
	int year = (DATE%100)+2000;
	
	struct tm start_date = {0};
    start_date.tm_year = 1970 - 1900; 
    start_date.tm_mon = 0;  
    start_date.tm_mday = 1;
    
	struct tm end_date = {0};
    end_date.tm_year = year - 1900;
    end_date.tm_mon = month-1;  
    end_date.tm_mday = day;
    int days = days_between(start_date, end_date);
    
    year = days*86400;
    GPS_variable[1] = year+hour+min+sec;
    

}

void latitude()
{
	GPS_variable[8] = NMEA[9][0] - '0';
	
    if (NMEA[3][0] == '\0') {
        return;
    }

    char *token = strtok(NMEA[3], ".");
    if (token == NULL) {
        return;
    }

    char BT[10];
    strcpy(BT, token);

    token = strtok(NULL, ".");
    if (token == NULL) {
        return;
    }

    char AT[10];
    strcpy(AT, token);

    int lat1 = (int) strtol(BT, NULL, 10);
    int lat2 = (int) strtol(AT, NULL, 10);
    float raw_latitude = (int) (lat1 * (int) pow(10, strlen(AT)) + lat2);
    int Flatitude;
    float Blatitude;
    raw_latitude = raw_latitude*0.00001;
    Flatitude = (raw_latitude/100);
    Blatitude = fmod(raw_latitude, 100.0);
    GPS_variable[2] = (Flatitude+(Blatitude/60))*1000000;
    
}

void longitude()
{
	GPS_variable[9] = NMEA[10][0] - '0';

    char *token = strtok(NMEA[4], ".");
    if (token == NULL) {
        return;
    }

    char BG[10];
    strcpy(BG, token);

    token = strtok(NULL, ".");
    if (token == NULL) {
        return;
    }

    char AG[10];
    strcpy(AG, token);

    int lon1 = (int) strtol(BG, NULL, 10);
    int lon2 = (int) strtol(AG, NULL, 10);
    float raw_longitude = (int) (lon1 * (int) pow(10, strlen(AG)) + lon2);
    int Flongitude;
    float Blongitude;
    raw_longitude = raw_longitude*0.00001;
    Flongitude = (raw_longitude/100);
    Blongitude = fmod(raw_longitude, 100.0);
    GPS_variable[3] = (Flongitude+(Blongitude/60))*1000000;
}


void *Log(void *arg) {
    FILE *log_file;
    char filename[100];  
    time_t now;
    struct tm *tm_info;

    struct mq_attr attributes = {
        .mq_flags = 0,
        .mq_maxmsg = 10,
        .mq_curmsgs = 0,
        .mq_msgsize = sizeof(Message)
    };

    Message send_msg = {0};
    Message receive_msg = {0};

    time(&now);

    mqd_t mq_send_log = mq_open("/mq_telecommand_send_log", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);
    if (mq_send_log == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }

    mqd_t mq_return = mq_open("/mq_return", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);
    if (mq_return == -1) {
        perror("mq_open /mq_return");
        exit(EXIT_FAILURE);
    }

    while (1) {
        if (mq_receive(mq_send_log, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) {
            perror("mq_receive");
            exit(EXIT_FAILURE);
        }

        if (receive_msg.req_id == 3 && (receive_msg.param >= 5 && receive_msg.param <= 60)) {
            printf("Start Log\n");
            snprintf(filename, sizeof(filename), "gps_log_%ld.txt", (long)now);
            log_file = fopen(filename, "w");
            if (log_file == NULL) {
                perror("Error opening log file");
                exit(EXIT_FAILURE);
            }
            fprintf(log_file, "Start Log Time: %ld\n", (long)now);
            fprintf(log_file, "1, 0, 1, 2, \"Status\", 0, 1,0, []\n");
            fprintf(log_file, "1, 0, 1, 2, \"Time\", 0, 1,0, []\n");
            fprintf(log_file, "1, 0, 1, 3, \"Latitude\", 0, 0.000001, -180, degrees\n");
            fprintf(log_file, "1, 0, 1, 5, \"Longitude\", 0, 0.000001, -90, degrees\n\n");
            fflush(log_file);

            // Send confirmation back for start log
            send_msg = receive_msg;
            send_msg.param = 1;
            send_msg.type = 3;
            send_msg.req_id = 3;
            if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                perror("mq_send start_log");
                exit(EXIT_FAILURE);
            }

            while (1) {
                printf("Logging...\n");
                time(&now);
                fprintf(log_file, "%ld, ", (long)now);
                fprintf(log_file, "%u, ", GPS_variable[0]);
                fprintf(log_file, "%u, ", GPS_variable[1]);
                fprintf(log_file, "%u, ", GPS_variable[2]);
                fprintf(log_file, "%u, \n", GPS_variable[3]);
                fflush(log_file);
                sleep(receive_msg.param);

                struct timespec ts;
                clock_gettime(CLOCK_REALTIME, &ts);
                ts.tv_sec += 1;

                if (mq_timedreceive(mq_send_log, (char *)&receive_msg, sizeof(receive_msg), NULL, &ts) != -1) {
                    if (receive_msg.req_id == 4) {
                        printf("Stop Log\n");
                        fclose(log_file);

                        // Send confirmation back for stop log
                        send_msg = receive_msg;
                        send_msg.param = 1;
                        send_msg.type = 3;
                        send_msg.req_id = 4;
                        if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                            perror("mq_send stop_log");
                            exit(EXIT_FAILURE);
                        }

                        break;
                    }
                }
            }
        }
    }

    mq_close(mq_send_log);
    mq_unlink("/mq_telecommand_send_log");
    mq_close(mq_return);
    mq_unlink("/mq_return");
    return NULL;
}


// ? GPS.c - update_variable()
void *update_variable(void *arg) {
    int fd = OpenGPSPort("/dev/ttyAMA0");

    struct mq_attr attributes = {
        .mq_flags = 0,
        .mq_maxmsg = 10,
        .mq_curmsgs = 0,
        .mq_msgsize = sizeof(Message)
    };

    Message send_msg = {0};
    Message receive_msg = {0};

    mqd_t mq_send_read = mq_open("/mq_telecommand_send_read", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);
    if (mq_send_read == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }

    mqd_t mq_return = mq_open("/mq_return", O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, &attributes);
    if (mq_return == -1) {
        perror("mq_open");
        exit(EXIT_FAILURE);
    }

    while (1) {
        status();
        latitude();
        longitude();

        if (GPS_variable[0] != 0) {
            GPS_variable[12] = 1;

            if (GPS_variable[12] == 1 && GPS_variable[0] == 1) {
                if (mq_receive(mq_send_read, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) {
                    perror("mq_receive");
                    exit(EXIT_FAILURE);
                }
			}

                send_msg = receive_msg;
                if (receive_msg.req_id == 1 && GPS_variable[12] == 1) {
                    // ? ???????????? GPS ????
                    send_msg.param = 1;
                    send_msg.type = 3;
                    printf("[GPS] Sampling Start - Param: %u\n", send_msg.param);
                    if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                        perror("mq_send");
                        exit(EXIT_FAILURE);
                    }

                    while (1) {
                        GPS_variable[0] = 2;
                        GPS_time();
                        latitude();
                        longitude();

                        struct timespec ts;
                        clock_gettime(CLOCK_REALTIME, &ts);
                        ts.tv_sec += 1;
                        if (mq_timedreceive(mq_send_read, (char *)&receive_msg, sizeof(receive_msg), NULL, &ts) != -1) {
                            if (receive_msg.req_id == 2) {
                                send_msg.param = 1;
                                send_msg.type = 3;
                                printf("[GPS] Stop Sampling\n");
                                memset(GPS_variable, 0, sizeof(GPS_variable));
                                if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                                    perror("mq_send");
                                    exit(EXIT_FAILURE);
                                }

                                break;
                            }
                            else if (receive_msg.req_id != 2){
                              send_msg = receive_msg;
                              send_msg.param = 0;
                              send_msg.type = 3;
                              printf("[GPS] Deny Request - Param: 0\n");
                              if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                                  perror("mq_send (deny)");
                                  exit(EXIT_FAILURE);
                              }
                        
                            }
                        }
                        
                    }
                }
                else {
            // ? GPS ??????????? - ??????? param = 0

                send_msg = receive_msg;
                send_msg.param = 0;
                send_msg.type = 3;
                printf("[GPS] Deny Request - Param: 0\n");
                if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                    perror("mq_send (deny)");
                    exit(EXIT_FAILURE);
                }
            
        }
            
        } 
        else {
            // ? GPS ??????????? - ??????? param = 0
                if (mq_receive(mq_send_read, (char *)&receive_msg, sizeof(receive_msg), NULL) == -1) {
                    perror("mq_receive (deny)");
                    exit(EXIT_FAILURE);
                }
                send_msg = receive_msg;
                send_msg.param = 0;
                send_msg.type = 3;
                printf("[GPS] Deny Request - Param: 0\n");
                if (mq_send(mq_return, (char *)&send_msg, sizeof(send_msg), 1) == -1) {
                    perror("mq_send (deny)");
                    exit(EXIT_FAILURE);
                }
            
        }
    }

    mq_close(mq_send_read);
    mq_close(mq_return);
    mq_unlink("/mq_return");
    mq_unlink("/mq_telecommand_send_read");
    return NULL;
}



    
    



void *read_GPS(void *arg) {
    int fd = -1; // Initialize fd as -1
    char buffer[255];
    int nbytes;
    char *field[MAX_FIELDS];
    int comma;
    if ((fd = OpenGPSPort("/dev/ttyAMA0")) < 0) 
    {
        printf("Cannot open GPS port\r\n.");
        return NULL;
    }

	do {
	    if ((nbytes = read(fd, &buffer, sizeof(buffer))) < 0) 
		{
	        perror("Read");
	        return NULL;
	    } 
		else 
		{
	        if (nbytes == 0) 
			{
	            printf("No communication from GPS module\r\n");
	            sleep(1);
	        } 
			else 
			{
	            buffer[nbytes - 1] = '\0';
	            if (checksum_valid(buffer)) 
				{
	                if ((strncmp(buffer, "$GP", 3) == 0)) 
					{
	                	comma = parse_comma_delimited_str(buffer, field, MAX_FIELDS);
	                    	if (strncmp(&buffer[3], "RMC", 3) == 0) 
							{   
		                        strcpy(NMEA[0], field[2]);//Status
		                        strcpy(NMEA[1], field[1]);//UTC
		                        strcpy(NMEA[2], field[9]);//Date
		                        strcpy(NMEA[3], field[3]);//Latitude
		                        strcpy(NMEA[4], field[5]);//Longitude
		                        strcpy(NMEA[8], field[8]);//COGs
		                        strcpy(NMEA[9], field[4]);//Direction N/S
		                        strcpy(NMEA[10], field[6]);//Direction E/W
		                        strcpy(NMEA[11], field[7]);//SOG
		                        //printf("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s*%s\n",field[0],field[1],field[2],field[3],field[4],field[5],field[6],field[7],field[8],field[9],field[10],field[11],field[12],field[13]);
		                    }
		                    if (strncmp(&buffer[3], "GGA", 3) == 0) 
							{
		                        strcpy(NMEA[5], field[9]);//Altitude
		                        strcpy(NMEA[6], field[7]);//SOT
		                        strcpy(NMEA[7], field[8]);//HDOP
		                    }
	                }
	            }
	        }
	    }
	} while(1);
	
	return NULL;
}

int OpenGPSPort(const char *devname)
{
    int fd;
    struct termios options;

    if ((fd = open(devname, O_RDWR | O_NOCTTY | O_NDELAY)) < 0)
    {
        perror("Open");
        return -1; // Return -1 to indicate failure
    }

    // Set to blocking mode
    fcntl(fd, F_SETFL, 0);

    // Get port attributes
    tcgetattr(fd, &options);

    // Set input and output baud rates to 9600
    cfsetispeed(&options, B9600);
    cfsetospeed(&options, B9600);

    // Set 8 bits, no parity, 1 stop bit
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;

    // Set input mode
    options.c_iflag |= ICRNL;

    // Set local mode
    options.c_lflag &= ~ECHO;
    options.c_lflag |= ICANON;

    // Set port attributes
    tcsetattr(fd, TCSAFLUSH, &options);

    return fd; // Return fd as int
}
int hexchar2int(char c)
{
    if (c >= '0' && c <= '9')
        return c - '0';
    if (c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    if (c >= 'a' && c <= 'f')
        return c - 'a' + 10;
    return -1;
}

// Function to convert hexadecimal string to integer
int hex2int(char *c)
{
    int value;
    value = hexchar2int(c[0]);
    value = value << 4;
    value += hexchar2int(c[1]);
    return value;
}

// Function to validate checksum
int checksum_valid(char *string)
{
    char *checksum_str;
    int checksum;
    unsigned char calculated_checksum = 0;

    checksum_str = strchr(string, '*');
    if (checksum_str != NULL) {
        *checksum_str = '\0';
        for (int i = 1; i < strlen(string); i++) {
            calculated_checksum ^= string[i];
        }
        checksum = hex2int(checksum_str + 1);
        if (checksum == calculated_checksum) {
            return 1;
        }
    }
    return 0;
}

// Function to parse comma-delimited string
int parse_comma_delimited_str(char *string, char **fields, int max_fields)
{
    int i = 0;
    fields[i++] = string;
    while ((i < max_fields) && (string = strchr(string, ',')) != NULL) {
        *string = '\0';
        fields[i++] = ++string;
    }
    return i - 1;
}
