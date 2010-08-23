// LAD-SPEKTROMETER
// 2010

#include "avr/io.h"
#include <avr/interrupt.h>
#include "stdlib.h"
#include "math.h"

#define F_CPU 16000000UL
#include <util/delay.h>
 
#define UART_UBRR_CALC(BAUD_,FREQ_) ((FREQ_)/((BAUD_)*16L)-1) 
#define UART_BAUD_RATE		19200
#define UART_BUFFER		10

// Pins definieren:

#define	SW1		PD3	//	B
#define	SW2		PD2	//	A


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

void switch_led (uint8_t n_led)
// Schaltet zwischen den Leds
{
	switch (n_led)
	{
		case 0:
			PORTD &= ~(1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 1:
			PORTD &= ~(1 << SW1);
			PORTD |= (1 << SW2);
		break;
		case 2:
			PORTD |= (1 << SW1);
			PORTD &= ~(1 << SW2);
		break;
		case 3:
			PORTD |= (1 << SW1);
			PORTD |= (1 << SW2);
		break;
	}
}

void init (void)
// initialisiere alle Ein/Ausgänge
{
	DDRD |= (1 << SW1);
	DDRD |= (1 << SW2);
		
	uart_init(1, 1);
}

// main:
int main (void)
{
	init();
	uint8_t task;
	uint8_t in_type		= 0;
	uint8_t i; uint8_t j;
	
	while (1)
   	{
   		// pollen
   		task = uart_getc();
   		
   		if (task == '!')
   		// Leds ausmessen und Werte senden
   		{
   			for (in_type = 0; in_type <= 3; in_type++)
   			{
   				for (i = 0; i < 4; i++)
   				{
   					switch_led (i);
   				
   					 uart_puti(adc(in_type)); uart_putc(',');
				}
   			}
   			uart_putc(':');

   		}
   		else if (task == '?')
   		// Identifikation
   		{
   			uart_puts("$LAD-spectralanalyzer online:\n\r");
   		}
	} // end while
} // end main
