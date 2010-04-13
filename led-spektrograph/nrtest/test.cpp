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
	NRMat<DP> A(n, m);
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
	NRVec<DP> error_estimate(1., n);
	for (int i = 0; i < n; i++) error_estimate[i] = 0.4 * A_rowsum[i];
	
	this->A = A;
	this->A_rowsum = A_rowsum;
	this->lambda = lambda;
	this->n = n;
	this->m = m;
	this->error_estimate = error_estimate;
	backus_gilbert_smooth = -1.;
}


void DataSpectral::signal_from_spectrum(NRVec<DP> spectrum, NRVec<DP> &signal)
{
	signal = dot(A, spectrum);
}



void DataSpectral::spectrum_backus_gilbert(NRVec<DP> signal,
	NRVec<DP> &spectrum, double smooth)
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
			NRMat<DP> W(n, n);
			double s = 1.;
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
							double delta_lambda = lambda[y] - lambda[x];
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
			double denominator = dot(A_rowsum, W_inv_R);
			for (int i = 0; i < n; i++) BG[x][i] = W_inv_R[i] / denominator;
		}
	}
		
	// (NR 19.6.13)
	spectrum = dot(BG, signal);
}



double testfunc(double x)
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
	
	vector<double> xvec, yvec;
	
	while (fin.peek() != -1)
	{
		if (fin.peek() == 35 or fin.peek() == 10)
		{
			// skip comment and empty lines
			char line[100];
			fin.getline(line, 100);
			continue;
		}
		char line[100];
		fin.getline(line, 100);
		double a, b;
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

double dot(const NRVec<DP> &a, const NRVec<DP> &b)
{
	if (a.size() != b.size())
		std::cerr << "vectors are not aligned!" << std::endl;
	double c = 0.;
	for (int i = 0; i < a.size(); i++)
	{
		c += a[i] * b[i];
	}
	return c;
}
