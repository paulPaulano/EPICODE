#include <stdio.h>
#include <stdlib.h>

int	main(int argc, char **argv)
{	
	if (argc < 3)
	{
		printf("Inserisci due numeri da moltiplicare...\n");
		return 1;
	}
	else if (argc > 3)
	{
		printf("Hai inserito un numero di troppo...\n");
		return 1;
	}
	int	primo = atoi(argv[1]);
	int	secondo = atoi(argv[2]);
	int	risultato = primo * secondo;

	printf("Il risultato è: %d\n", risultato);
}

