// C program to find area
// of circle
#include <math.h>
#include <stdio.h>
#define PI 3.142

double findArea(int r) { return PI * pow(r, 2); }

int main()
{
    printf("Area is %f", findArea(5));
    return 0;
}
