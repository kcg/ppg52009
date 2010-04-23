#include "test.h"
#include <math.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cstdlib>
#include <vector>


#include "nr/nr.h"
#include "nr/nrutil.h"


// Die jeweilige .cpp Datei von numerical recipes muss dem compiler mit übergeben werden
// nr/gaussj.cpp nr/amoeba.cpp nr/amotry.cpp


// We use global variables here for the fit-algorithms.
// This is bad but it's the only way to work with
// second edition numerical recipes code
double global_n;
double global_m;
NRMat<DP> global_A;
NRVec<DP> global_lambda;
NRVec<DP> global_signal;
NRVec<DP> global_error;



DataSpectral::DataSpectral()
{
	int n, m;
	vector<NRVec<DP> > xv, yv;
	string folder = "spektren";
	char *(fnames[]) = { "180391.dat", "180567.dat", "180575.dat",
		"epd470.dat", "LGT676.dat", "LPM675.dat", "LVT67C.dat",
		"LYT676.dat", "rlcv415a.dat", "smc660.dat", "smc680.dat",
		"smc700.dat", "smc720.dat", "smd-led3528RT.dat", "smt735.dat",
		"vl400_2.dat"};
	for (int i = 0; i < sizeof(fnames) / sizeof(char*); i++)
	{
		NRVec<DP> x, y;
		readfile(folder + "/" + fnames[i], x, y);
		xv.push_back(x);
		yv.push_back(y);
	}
	n = yv.size();
	m = yv[0].size();
	NRMat<DP> A(0., n, m);
	NRVec<DP> A_rowsum(0., n);
	NRVec<DP> lambda(m);
	for (int j = 0; j < m; j++)
	{
		for (int i = 0; i < n; i++)
		{
			A[i][j] = yv[i][j];
			A_rowsum[i] += yv[i][j];
		}
		lambda[j] = xv[0][j];
	}
	NRVec<DP> error_estimate(0.2, n);
	for (int i = 0; i < n; i++) error_estimate[i] = 0.4 * A_rowsum[i];
	
	this->A = A; global_A = A;
	this->A_rowsum = A_rowsum;
	this->lambda = lambda; global_lambda = lambda;
	this->n = n; global_n = n;
	this->m = m; global_m = m;
	this->error_estimate = error_estimate; global_error = error_estimate;
	backus_gilbert_smooth = -1.;
}


void DataSpectral::signal_from_spectrum(NRVec<DP> spectrum, NRVec<DP> &signal)
{
	signal = dot(A, spectrum);
}



void DataSpectral::spectrum_backus_gilbert(NRVec<DP> signal,
	NRVec<DP> &spectrum, DP smooth)
{
	// calculates a spectrum using the backus-gilbert method
	// the result will be written to "spectrum"
	// (NR 19.6)
		
	if (backus_gilbert_smooth != smooth)
	{
		backus_gilbert_smooth = smooth;
		// create a new backus-gilbert matrix BG
		BG = NRMat<DP>(m, n);
		for (int x = 0; x < m; x++)
		{
			NRMat<DP> W(0., n, n);
			DP s = 1.;
			if (smooth != 1.)
			{
				s = smooth / (1. - smooth);
				s *= s;
				
				for (int i = 0; i < n; i++)
				{
					for (int j = 0; j < n; j++)
					{
						for (int y = 0; y < m; y++)
						{
							// (NR 19.6.10)
							DP delta_lambda = lambda[y] - lambda[x];
							W[i][j] += sqr(delta_lambda) * A[i][y] * A[j][y];
						}
					}
				}
			}
			
			// add error matrix S to W
			// (NR 19.6.11)
			for (int i = 0; i < n; i++)
			{
				W[i][i] += s * sqr(error_estimate[i]);
			}
			// W is now W + s * S
			
			// (part of NR 19.6.12)
			NRMat<DP> Rmat(n, 1);
			for (int i = 0; i < n; i++)
			{
				Rmat[i][0] = A_rowsum[i];
			}
			NR::gaussj(W, Rmat);
			NRVec<DP> W_inv_R(n);
			for (int i = 0; i < n; i++) W_inv_R[i] = Rmat[i][0];
			
			// (NR 19.6.12 BG consists of all vectors q(x))
			DP denominator = dot(A_rowsum, W_inv_R);
			for (int i = 0; i < n; i++) BG[x][i] = W_inv_R[i] / denominator;
		}
	}
		
	// (NR 19.6.13)
	spectrum = dot(BG, signal);
}

// planck spectrum of a black body
DP f_blackbody(const DP x, Vec_I_DP &a)
{
	// x: wavelength lambda in nanometers
	DP lambda = 1e-9 * x;
	DP h = 6.6261e-34;
	DP c = 2.9979e8;
	DP k = 1.3807e-23;
	// a[0] is the scaling factor
	DP T = a[1]; // temperature
	if (T < 1.) T = 1.;
	DP hclkT = abs((h * c) / (lambda * k * a[1]));
	DP ex = exp(hclkT);
	// scale the function to a reasonable range
	DP f1 = pow(lambda * T, -5) / 3.5e10;
	DP f2;
	if (hclkT > 1e-8)
		f2 = 1. / (ex - 1.);
	else
		f2 = 1. / hclkT; // use Taylor approximation
	return exp(a[0]) * f1 * f2;
}

// merit function for the fit algorithm
// uses global variables because they can't be passed by minimizer
DP chisq_blackbody(Vec_I_DP &params)
{
	NRVec<DP> bb_spec(global_m);
	for (int i = 0; i < global_m; i++)
		bb_spec[i] = f_blackbody(global_lambda[i], params);
	NRVec<DP> signal_theo = dot(global_A, bb_spec);
	DP chisq = 0.;
	for (int i = 0; i < global_n; i++)
		chisq += sqr((signal_theo[i] - global_signal[i]) / global_error[i]);
	
	return chisq;
}

void DataSpectral::spectrum_blackbody(NRVec<DP> signal,
	NRVec<DP> &spectrum, DP &temperature, DP &chisq)
{
	// calculates the best-fit blackbody spectrum
	// uses downhill simplex algorithm
	// the result will be written to "spectrum"
	// the best-fit temperature will be written to "temperature"
	// the chi-square value will be written to "chisq"
	
	global_signal = signal;

	const int npar = 2;
	NRMat<DP> p(npar+1, npar);
	NRVec<DP> y(npar+1), p_vec(npar), spec(m);
	p[0][0] = 1.; p[0][1] = 5400;
	p[1][0] = 1.5; p[1][1] = 5500;
	p[2][0] = 1.; p[2][1] = 5600;
	for (int i = 0; i <= npar; i++)
	{
		for (int j = 0; j < npar; j++) p_vec[j] = p[i][j];
		y[i] = chisq_blackbody(p_vec);
	}
	int nfunc;
	NR::amoeba(p, y, sqr(1e-5), chisq_blackbody, nfunc);
	int i_min = 0;
	for (int i = 1; i <= npar; i++) if (y[i] < y[i_min]) i_min = i;
	for (int i = 0; i < 2; i++) p_vec[i] = p[i_min][i];
	for (int i = 0; i < m; i++) spec[i] = f_blackbody(lambda[i], p_vec);
	spectrum = spec;
	temperature = p[i_min][1];
	chisq = y[i_min];
}




// gauss curve
DP f_gauss(const DP x, Vec_I_DP &a)
{
	if (a[2] == 0) return a[0];
	return exp(a[0] - sqr((x - a[1]) * a[2]));
}

// merit function for the fit algorithm
// uses global variables because they can't be passed by minimizer
DP chisq_gauss(Vec_I_DP &params)
{
	NRVec<DP> bb_spec(global_m);
	for (int i = 0; i < global_m; i++)
		bb_spec[i] = f_gauss(global_lambda[i], params);
	NRVec<DP> signal_theo = dot(global_A, bb_spec);
	DP chisq = 0.;
	for (int i = 0; i < global_n; i++)
		chisq += sqr((signal_theo[i] - global_signal[i]) / global_error[i]);
	
	return chisq;
}

void DataSpectral::spectrum_gauss(NRVec<DP> signal,
	NRVec<DP> &spectrum, DP &lamb, DP &chisq)
{
	// calculates the best-fit gauss-shape spectrum
	// uses downhill simplex algorithm
	// the result will be written to "spectrum"
	// the best-fit wavelength will be written to "lamb"
	// the chi-square value will be written to "chisq"
	
	global_signal = signal;

	const int npar = 3;
	NRMat<DP> p(npar+1, npar);
	NRVec<DP> y(npar+1), p_vec(npar), spec(m);
	p[0][0] = 1.; p[0][1] = 540.; p[0][2] = 1./400.;
	p[1][0] = 1.5; p[1][1] = 540.; p[1][2] = 1./400.;
	p[2][0] = 1.; p[2][1] = 580.; p[2][2] = 1./400.;
	p[3][0] = 1.; p[3][1] = 540.; p[3][2] = 1./410.;
	for (int i = 0; i <= npar; i++)
	{
		for (int j = 0; j < npar; j++) p_vec[j] = p[i][j];
		y[i] = chisq_gauss(p_vec);
	}
	int nfunc;
	NR::amoeba(p, y, sqr(1e-4), chisq_gauss, nfunc);
	int i_min = 0;
	for (int i = 1; i <= npar; i++) if (y[i] < y[i_min]) i_min = i;
	for (int i = 0; i < npar; i++) p_vec[i] = p[i_min][i];
	for (int i = 0; i < m; i++) spec[i] = f_gauss(lambda[i], p_vec);
	spectrum = spec;
	lamb = p[i_min][1];
	chisq = y[i_min];
}



DP testfunc(DP x)
{
	return exp(-pow((x - 500.) / 100., 2)) + exp(-pow((x - 630.) / 15., 2));
}



int main()
{
	DataSpectral D;
	
	NRVec<DP> spec0(D.getm());
	ofstream f1("data1.dat");
	for (int i = 0; i < D.getm(); i++)
	{
		spec0[i] = testfunc(D.getlambda()[i]);
		f1 << D.getlambda()[i]; f1 << "\t"; f1 << spec0[i]; f1 << "\n";
	}

	NRVec<DP> sig;
	D.signal_from_spectrum(spec0, sig);
	ofstream f2("data2.dat");
	for (int i = 0; i < D.getn(); i++)
	{
		f2 << sig[i]; f2 << "\n";
	}
	
	std::cout << std::endl;
	NRVec<DP> spec1;
	D.spectrum_backus_gilbert(sig, spec1, 0.5);
	ofstream f3("data3.dat");
	for (int i = 0; i < D.getm(); i++)
	{
		f3 << D.getlambda()[i]; f3 << "\t"; f3 << spec1[i];	f3 << "\n";
	}
	
	std::cout << std::endl;
	NRVec<DP> spec2;
	DP T, chisq;
	D.spectrum_blackbody(sig, spec2, T, chisq);
	ofstream f4("data4.dat");
	for (int i = 0; i < D.getm(); i++)
	{
		f4 << D.getlambda()[i]; f4 << "\t"; f4 << spec2[i];	f4 << "\n";
	}
	std::cout << "T = " << T << std::endl;
	std::cout << "chisq = " << chisq << std::endl;
	
	
	std::cout << std::endl;
	NRVec<DP> spec3;
	DP lamb;
	D.spectrum_gauss(sig, spec3, lamb, chisq);
	ofstream f5("data5.dat");
	for (int i = 0; i < D.getm(); i++)
	{
		f5 << D.getlambda()[i]; f5 << "\t"; f5 << spec3[i];	f5 << "\n";
	}
	std::cout << "l = " << lamb << std::endl;
	std::cout << "chisq = " << chisq << std::endl;
	
}


void printmatrix(NRMat<DP> &A)
{
	for (int i = 0; i < A.nrows(); i++)
	{
		for (int j = 0; j < A.ncols(); j++)
		{
			std::cout << "\t" <<  A[i][j];
		}
		std::cout << std::endl;
	}
	std::cout << std::endl;
}






void readfile(string fname, NRVec<DP> &x, NRVec<DP> &y)
{
	ifstream fin(fname.c_str());
	if (!fin)
	{
		std::cerr << "Error opening input stream " << fname << std::endl;
		return;
	}
	
	vector<DP> xvec, yvec;
	
	while (fin.peek() != -1)
	{
		if (fin.peek() == 35 || fin.peek() == 10)
		{
			// skip comment and empty lines
			char line[100];
			fin.getline(line, 100);
			continue;
		}
		char line[100];
		fin.getline(line, 100);
		DP a, b;
		istringstream str(line);
		str >> a >> b;
		xvec.push_back(a);
		yvec.push_back(b);
	}
	
	x = NRVec<DP>(xvec.size());
	y = NRVec<DP>(yvec.size());
	for (int i = 0; i < xvec.size(); i++)
	{
		x[i] = xvec[i];
		y[i] = yvec[i];
	}
}



NRMat<DP> dot(const NRMat<DP> &A, const NRMat<DP> &B)
{
	if (A.ncols() != B.nrows())
		std::cerr << "matrices are not aligned!" << std::endl;
	NRMat<DP> C(A.nrows(), B.ncols());
	for (int i = 0; i < A.nrows(); i++)
	{
		for (int j = 0; j < B.ncols(); j++)
		{
			DP temp = 0.0;
			for (int k = 0; k < A.ncols(); k++)
			{
				temp += A[i][k] * B[k][j];
			}
			C[i][j] = temp;
		}
	}
	return C;
}

NRVec<DP> dot(const NRMat<DP> &A, const NRVec<DP> &b)
{
	if (A.ncols() != b.size())
		std::cerr << "matrices are not aligned!" << std::endl;
	NRVec<DP> c(A.nrows());
	for (int i = 0; i < A.nrows(); i++)
	{
		DP temp = 0.0;
		for (int k = 0; k < A.ncols(); k++)
		{
			temp += A[i][k] * b[k];
		}
		c[i] = temp;
	}
	return c;
}

DP dot(const NRVec<DP> &a, const NRVec<DP> &b)
{
	if (a.size() != b.size())
		std::cerr << "vectors are not aligned!" << std::endl;
	DP c = 0.;
	for (int i = 0; i < a.size(); i++)
	{
		c += a[i] * b[i];
	}
	return c;
}
