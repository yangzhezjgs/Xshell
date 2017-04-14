#include <stdio.h>
int cnt = 0;
void my_print();
int main(void)
{
	int i,j;
	for(i = 1;i <= 5;i++)
			for(j = 1;j <= 5;j++)
					my_print(i,j);
	return 0;
}

void my_print(int a,int b)
{
	cnt++;
	printf("outer loop %d,inner loop %d ,count %d\n",a,b,cnt);
}
