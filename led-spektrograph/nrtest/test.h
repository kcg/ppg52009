#include "nr/nrutil.h"

class DataSpectral
{
public:
	DataSpectral();
	const int getn() { return n; };
	const int getm() { return m; };
	const NRVec<DP> &getlambda() { return lambda; };
	const NRMat<DP> &getA() { return A; };
	void signal_from_spectrum(NRVec<DP> spectrum, NRVec<DP> &signal);
	void spectrum_backus_gilbert(NRVec<DP> signal, NRVec<DP> &spectrum, double smooth=0.5);
private:
	// number of channels and lenght of each channel
	int n, m;
	// vector of wavelength values in nm (length m)
	NRVec<DP> lambda;
	// error estimation for measurement values (lenght n)
	NRVec<DP> error_estimate;
	// matrix of absorption curves (size n x m)
	NRMat<DP> A;
	NRVec<DP> A_rowsum;
	// backus-gilbert matrix (size m x n)
	NRMat<DP> BG;
	double backus_gilbert_smooth;
};


void printmatrix(NRMat<DP> &A);
void readfile(string fname, NRVec<DP> &x, NRVec<DP> &y);

NRMat<DP> dot(const NRMat<DP> &A, const NRMat<DP> &B);
NRVec<DP> dot(const NRMat<DP> &A, const NRVec<DP> &b);
double dot(const NRVec<DP> &a, const NRVec<DP> &b);

inline double sqr(double x) { return x * x; };
