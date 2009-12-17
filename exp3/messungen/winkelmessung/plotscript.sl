require("isisscripts");

variable winkel = [320,
		   312,
		   310,
		   300,
		   290,
		   280,
		   270,
		   260,
		   250,
		   240,
		   230,
		   220,
		   210,
		   200];
variable spannung = [-0.46076,
		     -0.43808,
		     -0.43389,
		     -0.40434,
		     -0.37629,
		     -0.34870,
		     -0.31782,
		     -0.28531,
		     -0.25117,
		     -0.21793,
		     -0.18233,
		     -0.14521,
		     -0.10960,
		     -0.07157];
variable winkel2 = [200,
		    210,
		    220,
		    230,
		    240,
		    250,
		    260,
		    270,
		    280,
		    290,
		    300,
		    310,
		    312,
		    320];
variable spannung2 = [-0.05941,
		      -0.09767,
		      -0.13517,
		      -0.17319,
		      -0.20765,
		      -0.24314,
		      -0.27790,
		      -0.30995,
		      -0.34035,
		      -0.36939,
		      -0.39801,
		      -0.42530,
		      -0.43074,
		      -0.45389];

variable winkel_fein = [240,
			238,
			236,
			234,
			232,
			230,
			228,
			226,
			224,
			222,
			220,
			218,
			216,
			214,
			212,
			210,
			208,
			206,
			204,
			202,
			200];
variable spannung_fein = [-0.21733,
			  -0.21031,
			  -0.20281,
			  -0.19582,
			  -0.18908,
			  -0.18246,
			  -0.17361,
			  -0.16827,
			  -0.16020,
			  -0.15172,
			  -0.14440,
			  -0.13778,
			  -0.13056,
			  -0.12347,
			  -0.11545,
			  -0.10953,
			  -0.10125,
			  -0.09277,
			  -0.08426,
			  -0.07877,
			  -0.07176];
()=open_plot("winkel_spannung_grob.ps/cps");
xrange(190,330);
yrange(-0.5,0);
xlabel("Winkel");
ylabel("Spannung [V]");
title("Schwarz: im Uhrzeigersinn; Rot: gegen Uhrzeigersinn");
pointstyle(-4); connect_points(0); color(1); plot(winkel,spannung);
pointstyle(-4); connect_points(0); color(2); oplot(winkel2,spannung2);
close_plot;

()=open_plot("winkel_spannung_fein.ps/cps");
xrange(198,242);
yrange(-0.25,0);
xlabel("Winkel");
ylabel("Spannung [V]");
title("Schwarz: im Uhrzeigersinn");
pointstyle(-4); connect_points(0); color(1); plot(winkel_fein,spannung_fein);
close_plot;
exit;