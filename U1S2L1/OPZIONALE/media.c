#include <stdio.h>
#include <stdlib.h>

int	main(int argc, char* argv[])
{
	if (argc < 3)
	{
		printf("Inserire due numeri.\n");
		return 1;
	}
	else if (argc > 3)
	{
		printf("Hai inserito un numero di troppo.\n");
		return 1;
	}
	float	primo = atoi(argv[1]);
	float	secondo = atoi(argv[2]);
	float	media = (primo + secondo) / 2;
	
	printf("La media dei due numeri è:%.2f\n", media);
}
