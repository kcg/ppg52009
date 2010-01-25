// SPEKTRUM ANALYZER
// Controller: Atmega8; Taktrate: extern, 14.75 MHz Quarz; Baudrate: 9600
// Version: 10012010

#include "avr/io.h"
#include <avr/interrupt.h>
#include "stdlib.h"

#define F_CPU 14745600UL 		// 14.75 MHz Quarz
#include <util/delay.h>

#define UART_UBRR_CALC(BAUD_,FREQ_) ((FREQ_)/((BAUD_)*16L)-1) 
#define UART_BAUD_RATE		9600
#define UART_BUFFER		10

// Pins definieren:
#define	LED_ADC_0	0
#define LED_ADC_1	1
#define AREF_ADC	5
#define SW_AREF		PD6
#define SW_R		PD5
#define LED_IO		PD7
#define	SW0		PD4
#define	SW1		PD3
#define	SW2		PD2

#define R_FAC		10.0	//TODO!!



uint8_t uart_buffer[UART_BUFFER]; 
int8_t	uart_count  = 0;

ISR(SIG_UART_RECV) 
// INTERRUPT: speichere Zeichen vom UART in den Puffer
{
	if (uart_count < UART_BUFFER) uart_buffer[uart_count++] = UDR; 
} 

inline void uart_init(uint8_t tx, uint8_t rx) 
// initialisiert UART
{
	uint16_t baudrate; 
	// Baud-Rate setzen 
	baudrate = UART_BAUD_RATE/2; 
	UBRRH    = (uint8_t) (UART_UBRR_CALC(baudrate,F_CPU)>>8); 
	UBRRL    = (uint8_t) UART_UBRR_CALC(baudrate,F_CPU); 
	// TX und RX anschalten 
	UCSRA |= (1<<U2X); 
	UCSRB |= (1<<RXCIE); 
	if(tx) UCSRB |= (1<<TXEN); 
	if(rx) UCSRB |= (1<<RXEN); 
	sei(); 
	_delay_ms(1); 
}

inline uint8_t uart_getc(void)
// lese seriellen Port aus
{
	if (uart_count == 0) return 0; 
	return uart_buffer[--uart_count]; 
}

inline void uart_putc(uint8_t c)
// sendet einzelne Zeichen
{
	while (!(UCSRA & (1<<UDRE))); 
	UDR = c; 
}

void uart_puts(uint8_t *data)
// sendet string 
{
	while(*data) 
	{ 
		uart_putc(*data); 
		data++; 
	} 
}

inline void uart_puti(uint16_t data) 
// sendet integer per UART
{
	uint8_t buffer[7]; 
	uart_puts(utoa(data, buffer, 10)); 
}

void uart_putf(float data)
// sendet float per UART
{ 
	uint8_t buffer[7]; 
	uart_puts(dtostrf(data, 6, 2, buffer)); 
}

uint16_t adc (uint8_t admux) 
// ADC
{
	ADCSRA  =  (1<<ADEN)  | (1<<ADPS1) | (1<<ADPS0); 
	ADMUX   =  admux; 
	ADMUX  |=  (1<<REFS1) | (1<<REFS0); 
	ADCSRA |=  (1<<ADSC); 
	while      (ADCSRA    & (1<<ADSC)); 
	uint16_t val     = ADCW; 
	ADCSRA &= ~(1<<ADEN); 
	return val;
}

uint8_t switch_magnitude (uint8_t state)
// Schaltet den globalen Verstärkungsfaktor (R)
{
	if (state == 0)
	{
		PORTD &= ~(1 << SW_R);
		_delay_ms(1);
		return 0;
	}
	PORTD |= (1 << SW_R);
	_delay_ms(1);
	return 1;
}

uint8_t switch_aref (uint8_t state)
// Schaltet zwischen den AREF-Spannungen
{
	if (state == 0)
	{
		PORTD &= ~(1 << SW_AREF);
		_delay_ms(1);
		return 0;
	}
	PORTD |= (1 << SW_AREF);
	_delay_ms(1);
	return 1;
}

void switch_led (uint8_t n_led)
// Schaltet zwischen den Leds
{
	switch (n_led)
	{
		case 0:
			PORTD &= ~(1 << SW0);
			PORTD &= ~(1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 1:
			PORTD &= ~(1 << SW0);
			PORTD &= ~(1 << SW1);
			PORTD |= (1 << SW2);
		break;
		case 2:
			PORTD &= ~(1 << SW0);
			PORTD |= (1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 3:
			PORTD &= ~(1 << SW0);
			PORTD |= (1 << SW1);
			PORTD |= (1 << SW2);
		break;
		case 4:
			PORTD |= (1 << SW0);
			PORTD &= ~(1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 5:
			PORTD |= (1 << SW0);
			PORTD &= ~(1 << SW1);
			PORTD |= (1 << SW2);
		break;
		case 6:
			PORTD |= (1 << SW0);
			PORTD |= (1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 7:
			PORTD |= (1 << SW0);
			PORTD |= (1 << SW1);
			PORTD |= (1 << SW2);
		break;
	}
}

inline float get_aref_factor (uint8_t aref_state)
// gibt den Verstärkungsfaktor (AREF) zurück
{
	switch_aref (1);
	_delay_ms(1);
	float value0 = adc(AREF_ADC);
	return (1024.0 / value0);
	switch_aref(aref_state);
}

void init (void)
// initialisiere alle Ein/Ausgänge
{
	// Ausgänge aktivieren;
	DDRD |= (1 << SW_AREF);
	DDRD |= (1 << SW_R);
	DDRD |= (1 << LED_IO);
	DDRD |= (1 << SW0);
	DDRD |= (1 << SW1);
	DDRD |= (1 << SW2);
		
	uart_init(1, 1);
}

// main:
int main (void)
{
	init();
	
	uint8_t task;
	float aref_factor	= get_aref_factor(1);
	float val;
	uint8_t in_type		= 0;
	uint8_t value		= 0;
	uint8_t i;
	uint8_t j;
	
	uint8_t mul_r		= 0;	// 1: V_ref = 1, 0: 5 V_ref = 5
	uint8_t mul_a		= 0;	// 1: 1=1M (R) 0: 1=100kV (!R)
	
	uart_puts("spectral 0.5\n\r");
	PORTD |= (1 << LED_IO);
	
	
	while (1)
   	{
   		// pollen
   		task = uart_getc();
   		
   		if (task == '!')
   		// Leds ausmessen und Werte senden
   		{
   			uart_putc(':');
   			for (i = 0; i <= 8; i++)
   			{
   				for (in_type = 0; in_type <= 1; in_type++)
   				{
					for (j = 0; j < 2; j++)
					{
						value = adc(in_type);
					
						if ((mul_r == 1 && mul_a == 1) && value <= 20)
						{
							mul_r = switch_magnitude (0);
							// r -> 0, a -> 1
						}
						else if ((mul_r == 0 && mul_a == 1) && value <= 20)
						{
							mul_a = switch_aref (0);
							// r -> 0, a -> 0
						}
						else if ((mul_r == 0 && mul_a == 0) && value >= 1000)
						{
							mul_a = switch_aref (1);
							// r -> 0, a -> 1
						}
						else if ((mul_r == 0 && mul_a == 1) && value >= 1000)
						{
							mul_r = switch_magnitude (1);
							// r -> 1, a -> 1
						}
						_delay_ms(1);
					}	
					val =  (float) adc(in_type);
					if (!mul_r)	val *= R_FAC;
					if (!mul_a)	val *= aref_factor;
					uart_putf(val);
					uart_putc(';');	
				}
   			}
   		}
   		else if (task == '.')
   		// Verstärkungsfaktor für AREF zurückgeben
   		{
   			aref_factor	= get_aref_factor(mul_a);
   			uart_putf(aref_factor);
   			uart_puts("\n\r");
   		}
   		else if (task == '?')
   		// Identifikation
   		{
   			uart_puts("spectral-analyzer 0.1 up and running\n\r");
   		}

	} // end while
} // end main
