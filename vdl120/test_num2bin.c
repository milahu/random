/*

this code is part of the "vdl120" project

public domain + no warranty

gcc -o test_num2bin test_num2bin.c && ./test_num2bin

version 2019-07-25 by milahu at gmail

TODO byte order
make the vdl120 code
1. work with climate logger sticks
2. independent of the host byte order

*/



/* printf */
#include <stdio.h>

/* malloc */
#include <stdlib.h>



/* convert to/from cryptic integer encoding */

short int num2bin(short int);
short int bin2num(short int);



/* conversion table */

#define NUM2BIN_MAX 100
#define SIGN_BIT 0x8000 /* 1 << 15 */

/* force byte order (endianness) by casting char -> short int */
#define num2bin_data ((short int *)num2bin_data_char)
char num2bin_data_char[] = 
{
	0x00, 0x00, /*   0 */
	0x80, 0x3F, /*   1 */
	0x00, 0x40, /*   2 */
	0x40, 0x40, /*   3 */
	0x80, 0x40, /*   4 */
	0xA0, 0x40, /*   5 */
	0xC0, 0x40, /*   6 */
	0xE0, 0x40, /*   7 */
	0x00, 0x41, /*   8 */
	0x10, 0x41, /*   9 */
	0x20, 0x41, /*  10 */
	0x30, 0x41, /*  11 */
	0x40, 0x41, /*  12 */
	0x50, 0x41, /*  13 */
	0x60, 0x41, /*  14 */
	0x70, 0x41, /*  15 */
	0x80, 0x41, /*  16 */
	0x88, 0x41, /*  17 */
	0x90, 0x41, /*  18 */
	0x98, 0x41, /*  19 */
	0xA0, 0x41, /*  20 */
	0xA8, 0x41, /*  21 */
	0xB0, 0x41, /*  22 */
	0xB8, 0x41, /*  23 */
	0xC0, 0x41, /*  24 */
	0xC8, 0x41, /*  25 */
	0xD0, 0x41, /*  26 */
	0xD8, 0x41, /*  27 */
	0xE0, 0x41, /*  28 */
	0xE8, 0x41, /*  29 */
	0xF0, 0x41, /*  30 */
	0xF8, 0x41, /*  31 */
	0x00, 0x42, /*  32 */
	0x04, 0x42, /*  33 */
	0x08, 0x42, /*  34 */
	0x0C, 0x42, /*  35 */
	0x10, 0x42, /*  36 */
	0x14, 0x42, /*  37 */
	0x18, 0x42, /*  38 */
	0x1C, 0x42, /*  39 */
	0x20, 0x42, /*  40 */
	0x24, 0x42, /*  41 */
	0x28, 0x42, /*  42 */
	0x2C, 0x42, /*  43 */
	0x30, 0x42, /*  44 */
	0x34, 0x42, /*  45 */
	0x38, 0x42, /*  46 */
	0x3C, 0x42, /*  47 */
	0x40, 0x42, /*  48 */
	0x44, 0x42, /*  49 */
	0x48, 0x42, /*  50 */
	0x4C, 0x42, /*  51 */
	0x50, 0x42, /*  52 */
	0x54, 0x42, /*  53 */
	0x58, 0x42, /*  54 */
	0x5C, 0x42, /*  55 */
	0x60, 0x42, /*  56 */
	0x64, 0x42, /*  57 */
	0x68, 0x42, /*  58 */
	0x6C, 0x42, /*  59 */
	0x70, 0x42, /*  60 */
	0x74, 0x42, /*  61 */
	0x78, 0x42, /*  62 */
	0x7C, 0x42, /*  63 */
	0x80, 0x42, /*  64 */
	0x82, 0x42, /*  65 */
	0x84, 0x42, /*  66 */
	0x86, 0x42, /*  67 */
	0x88, 0x42, /*  68 */
	0x8A, 0x42, /*  69 */
	0x8C, 0x42, /*  70 */
	0x8E, 0x42, /*  71 */
	0x90, 0x42, /*  72 */
	0x92, 0x42, /*  73 */
	0x94, 0x42, /*  74 */
	0x96, 0x42, /*  75 */
	0x98, 0x42, /*  76 */
	0x9A, 0x42, /*  77 */
	0x9C, 0x42, /*  78 */
	0x9E, 0x42, /*  79 */
	0xA0, 0x42, /*  80 */
	0xA2, 0x42, /*  81 */
	0xA4, 0x42, /*  82 */
	0xA6, 0x42, /*  83 */
	0xA8, 0x42, /*  84 */
	0xAA, 0x42, /*  85 */
	0xAC, 0x42, /*  86 */
	0xAE, 0x42, /*  87 */
	0xB0, 0x42, /*  88 */
	0xB2, 0x42, /*  89 */
	0xB4, 0x42, /*  90 */
	0xB6, 0x42, /*  91 */
	0xB8, 0x42, /*  92 */
	0xBA, 0x42, /*  93 */
	0xBC, 0x42, /*  94 */
	0xBE, 0x42, /*  95 */
	0xC0, 0x42, /*  96 */
	0xC2, 0x42, /*  97 */
	0xC4, 0x42, /*  98 */
	0xC6, 0x42, /*  99 */
	0xC8, 0x42, /* 100 */
};

short int old_num2bin(short int num)
{
	if (num < -NUM2BIN_MAX || NUM2BIN_MAX < num)
	{
		printf("num2bin: cant convert number %i\n", num);
		return 0;
	}
	
	if (num < 0)
	{
		return num2bin_data[-num] | SIGN_BIT; // set sign bit
	}
	
	return num2bin_data[num];
}

short int old_bin2num(short int bin)
{
	int i, is_negative;
	
	/*
	printf("bin2num: bin =");
	for (i = 0; i < 32; i++)
	{
		if (i % 8 == 0)
			printf(" ");
		printf("%i", (bin>>i)&1);
	}
	printf("\n");
	*/
	
	is_negative = bin & SIGN_BIT;
	
	if (is_negative)
	{
		bin ^= SIGN_BIT; // unset sign bit
		//printf("bin2num: got negative number %x", bin);
	}
	
	for (i = 0; i <= NUM2BIN_MAX; i++)
	{
		if (num2bin_data[i] == bin)
		{
			if (is_negative)
				return -i;
			else
				return i;
		}
	}
	
	if (is_negative)
		printf("bin2num: cant convert data %x\n", bin | SIGN_BIT); // restore sign bit
	else
		printf("bin2num: cant convert data %x\n", bin);
	return 0;
}



/* new functions */

short int num2bin(short int num)
{
	short int bin = 0;
	char *pbin = NULL;
	pbin = (char *) &bin;

	// handle zero
	if (num == 0)
		return bin;

	// handle sign
	unsigned char sign = 0;
	if (num < 0)
	{
		sign = 1;
		num = -num;
	}

	// find first nonzero bit, 'lsb 0' bit numbering
	// num != 0 here
	char firstBit;
	for (firstBit=7; firstBit>=0; firstBit--)
	{
		if (((num >> firstBit) & 1) == 1)
			break;
	}
	
	// construct result:
	// bit 0    : sign bit
	// bit 1-8  : firstBit + 127
	// bit 9-15 : num without firstBit, left aligned

// TODO byte order
	//pbin[0] = (sign << 7) + ((firstBit + 127) >> 1);
	//pbin[1] = (((firstBit + 127) & 1) << 7) + ((num - (1 << firstBit)) << (7-firstBit));
	// change byte order
	pbin[1] = (sign << 7) + ((firstBit + 127) >> 1);
	pbin[0] = (((firstBit + 127) & 1) << 7) + ((num - (1 << firstBit)) << (7-firstBit));

	return bin;
}

short int bin2num(short int bin)
{
	char *pbin = NULL;

// TODO byte order
	//pbin = (char *) &bin;
	// change byte order
	pbin = malloc(2 * sizeof(char)); // free(pbin) later
	pbin[0] = ( (char *) &bin )[1];
	pbin[1] = ( (char *) &bin )[0];

	// zero
	if (bin == 0)
		return 0;

	// sign
	unsigned char sign = 0;
	sign = (pbin[0] >> 7) & 1;
	
	// num length
	char firstBit;
	firstBit = ((pbin[0] & 127) << 1) + ((pbin[1] & 128) >> 7) - 127;
	
	// result
	short int num;
	num = ((pbin[1] & 127) >> (7-firstBit)) + (1 << firstBit);

	// sign
	if (sign == 1)
		num = -num;

	free(pbin);

	return num;
}


//int test_num2bin()
int main()
{
	int n;
	int n2;
	int s;
	short int b;
	short int b2;

	// pass and fail counter
	int p = 0;
	int f = 0;

	for (n = 0; n <= 100; n++)
	{
		for (s=-1; s<=+1; s+=2) // s is -1 or +1
		{
			n = s * n; // add sign

			printf("n = %i\n", n);

			b = old_num2bin(n);

			b2 = num2bin(n);
			if (b == b2)
			{
				p++;
				printf("pass num2bin. old %4i --> %8x. new %4i --> %8x\n", n, b, n, b2);
			}
			else
			{
				f++;
				printf("fail num2bin. old %4i --> %8x. new %4i --> %8x\n", n, b, n, b2);
			}

			n2 = bin2num(b);
			if (n == n2)
			{
				p++;
				printf("pass bin2num. old %4i <-- %8x. new %4i <-- %8x\n", n, b, n2, b);
			}
			else
			{
				f++;
				printf("fail bin2num. old %4i <-- %8x. new %4i <-- %8x\n", n, b, n2, b);
			}

			n = s * n; // remove sign. -1 * -1 = +1
		}
	}
	printf("test done. %i pass + %i fail\n", p, f);
	return 0;
}

