// SPEKTRUM ANALYZER
// Controller: Atmega8, Taktrate: extern, 14.75 MHz Quarz, Baudrate: 2400
// Version: 06012010

#include "avr/io.h"
#include <avr/interrupt.h>
#include "stdlib.h"

#define F_CPU 14745600UL 		// 14.75 MHz Quarz
#include <util/delay.h>

#define UART_UBRR_CALC(BAUD_,FREQ_) ((FREQ_)/((BAUD_)*16L)-1) 
#define UART_BAUD_RATE		2400
#define UART_BUFFER		10

uint8_t uart_buffer[UART_BUFFER]; 
int8_t	uart_count  = 0;


uint8_t uart_getc(void)
// lese seriellen Port aus
{
	if (uart_count == 0) return 0; 
	return uart_buffer[--uart_count]; 
}

ISR(SIG_UART_RECV) 
// INTERRUPT: receive char from UART and save it the buffer
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

void uart_putc(uint8_t c)
// sendet einzelene Zeichen
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

void uart_puti(uint16_t data) 
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

void init (void)
// initialisiere alle Ein/Ausgänge
{
	// TODO
	
}

// main:
int main (void)
{
	init();
	uart_init(1, 1);
	
	while(1)
   	{
   		// TODO	        
	        
	}
} // end main
