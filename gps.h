#ifndef GPS_H
#define GPS_H

#define MAX_FIELDS 20
#include <time.h>
// ???????????? global ??????????????????
extern char NMEA[MAX_FIELDS][255];
extern int GPS_variable[20];
/*
GPS_variable[0] = GPS status
GPS_variable[1] = find GPS
GPS_variable[2] = GPS time
GPS_variable[3] = Latitude
GPS_variable[4] = Longitude
*/

// ?????????????????????? gps.c ??? TM_GPS.c
void *read_GPS(void *arg);
//void *Log(void *arg);
void *update_variable(void* arg);
void *Log(void *arg);
void status();
int days_between(struct tm start_date, struct tm end_date);
void GPS_time();
void latitude();
void longitude();
int checksum_valid(char *string);
int parse_comma_delimited_str(char *string, char **fields, int max_fields);
int OpenGPSPort(const char *devname);

#endif
