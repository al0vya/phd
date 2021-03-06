import os
import sys

def EXIT_HELP():
    help_message = (
        "This tool is used in the command line as follows:\n\n" +
        " - python test.py run <MODE> <SOLVER> <EPSILON> <MAX_REF_LVL> (runs all in-built test cases)\n" +
        "    MODE        : [debug,release]\n" +
        "    SOLVER      : [hw,mw]\n" +
        "    EPSILON     : [error threshold]\n" +
        "    MAX_REF_LVL : [maximum refinment level]\n" +
        "\n" +
        " - python test.py planar <MODE> <SOLVER> <TEST_CASE_DIR> <PHYS_QUANTITY> <INTERVAL> (plots planar solution)\n" +
        "    MODE          : [debug,release]\n" +
        "    SOLVER        : [hw,mw]\n" +
        "    PHYS_QUANTITY : [h,eta,qx,qy,z]\n" +
        "    INTERVAL      : [interval]\n" +
        "\n" +
        " - python test.py row_major <MODE> <PLOT_TYPE> (plots either solution surface or contours)\n" +
        "    MODE      : [debug,release]\n" +
        "    PLOT_TYPE : [cont,surf]\n" +
        "\n" +
        " - python test.py c_prop <MODE> <SOLVER> (plots discharge errors)\n" +
        "    MODE   : [debug,release]\n" +
        "    SOLVER : [hw,mw]"
    )

    sys.exit(help_message)

if len(sys.argv) < 3:
    EXIT_HELP()

import subprocess
import numpy             as np
import pandas            as pd
import matplotlib.pyplot as plt
import matplotlib.pylab  as pylab

from mpl_toolkits.mplot3d import Axes3D

def set_path(
    mode,
    testdir="test"
):
    if mode == "debug":
        path = os.path.join(os.path.dirname(__file__), "..", "out", "build", "x64-Debug", testdir, "results")
    elif mode == "release":
        path = os.path.join(os.path.dirname(__file__), "..", "out", "build", "x64-Release", testdir, "results")
    else:
        EXIT_HELP()
        
    return path

class PlanarSolution:
    def __init__(
        self,
        mode,
        solver,
        interval,
        testdir="test"
    ):
        if mode != "debug" and mode != "release":
            EXIT_HELP()
            
        if solver != "hw" and solver != "mw":
            EXIT_HELP()
            
        self.solver = solver
        
        self.interval = interval
        
        self.savepath = set_path(mode, testdir)
        
        planar_data_file = "planar-" + str(self.interval) + ".csv"
        
        print("Searching for data for PlanarSolution in path",  os.path.join(self.savepath, planar_data_file) )
        
        self.lower_left_x = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["lower_left_x"].values
        self.lower_left_y = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["lower_left_y"].values
        
        self.upper_right_x = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["upper_right_x"].values
        self.upper_right_y = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["upper_right_y"].values
        
        self.h0   = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["h0"].values
        self.h1x  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["h1x"].values  if solver == "mw" else None
        self.h1y  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["h1y"].values  if solver == "mw" else None
        
        self.qx0  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qx0"].values
        self.qx1x = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qx1x"].values if solver == "mw" else None
        self.qx1y = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qx1y"].values if solver == "mw" else None
        
        self.qy0  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qy0"].values
        self.qy1x = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qy1x"].values if solver == "mw" else None
        self.qy1y = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["qy1y"].values if solver == "mw" else None
        
        self.z0   = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["z0"].values
        self.z1x  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["z1x"].values  if solver == "mw" else None
        self.z1y  = pd.read_csv( os.path.join(self.savepath, planar_data_file) )["z1y"].values  if solver == "mw" else None
        
        self.num_cells = self.h0.size
        
        self.fig, self.ax = plt.subplots( subplot_kw={"projection" : "3d"} )
    
    def plot_soln(
        self,
        quantity
    ):
        print("Plotting planar solution...")

        S = None
        
        for cell in range(self.num_cells):
            print("Cell", cell + 1, "of", self.num_cells)
            
            x = [ self.lower_left_x[cell], self.upper_right_x[cell] ]
            y = [ self.lower_left_y[cell], self.upper_right_y[cell] ]
            
            X, Y = np.meshgrid(x, y)
            
            upper_left_h   = self.h0[cell]  - np.sqrt(3) * self.h1x[cell]  + np.sqrt(3) * self.h1y[cell]  if self.solver == "mw" else self.h0[cell]
            upper_right_h  = self.h0[cell]  + np.sqrt(3) * self.h1x[cell]  + np.sqrt(3) * self.h1y[cell]  if self.solver == "mw" else self.h0[cell]
            lower_left_h   = self.h0[cell]  - np.sqrt(3) * self.h1x[cell]  - np.sqrt(3) * self.h1y[cell]  if self.solver == "mw" else self.h0[cell]
            lower_right_h  = self.h0[cell]  + np.sqrt(3) * self.h1x[cell]  - np.sqrt(3) * self.h1y[cell]  if self.solver == "mw" else self.h0[cell]
            
            upper_left_qx  = self.qx0[cell] - np.sqrt(3) * self.qx1x[cell] + np.sqrt(3) * self.qx1y[cell] if self.solver == "mw" else self.qx0[cell]
            upper_right_qx = self.qx0[cell] + np.sqrt(3) * self.qx1x[cell] + np.sqrt(3) * self.qx1y[cell] if self.solver == "mw" else self.qx0[cell]
            lower_left_qx  = self.qx0[cell] - np.sqrt(3) * self.qx1x[cell] - np.sqrt(3) * self.qx1y[cell] if self.solver == "mw" else self.qx0[cell]
            lower_right_qx = self.qx0[cell] + np.sqrt(3) * self.qx1x[cell] - np.sqrt(3) * self.qx1y[cell] if self.solver == "mw" else self.qx0[cell]
            
            upper_left_qy  = self.qy0[cell] - np.sqrt(3) * self.qy1x[cell] + np.sqrt(3) * self.qy1y[cell] if self.solver == "mw" else self.qy0[cell]
            upper_right_qy = self.qy0[cell] + np.sqrt(3) * self.qy1x[cell] + np.sqrt(3) * self.qy1y[cell] if self.solver == "mw" else self.qy0[cell]
            lower_left_qy  = self.qy0[cell] - np.sqrt(3) * self.qy1x[cell] - np.sqrt(3) * self.qy1y[cell] if self.solver == "mw" else self.qy0[cell]
            lower_right_qy = self.qy0[cell] + np.sqrt(3) * self.qy1x[cell] - np.sqrt(3) * self.qy1y[cell] if self.solver == "mw" else self.qy0[cell]
            
            upper_left_z   = self.z0[cell]  - np.sqrt(3) * self.z1x[cell]  + np.sqrt(3) * self.z1y[cell]  if self.solver == "mw" else self.z0[cell]
            upper_right_z  = self.z0[cell]  + np.sqrt(3) * self.z1x[cell]  + np.sqrt(3) * self.z1y[cell]  if self.solver == "mw" else self.z0[cell]
            lower_left_z   = self.z0[cell]  - np.sqrt(3) * self.z1x[cell]  - np.sqrt(3) * self.z1y[cell]  if self.solver == "mw" else self.z0[cell]
            lower_right_z  = self.z0[cell]  + np.sqrt(3) * self.z1x[cell]  - np.sqrt(3) * self.z1y[cell]  if self.solver == "mw" else self.z0[cell]
            
            H  = np.asarray( [ [lower_left_h,  lower_right_h ], [upper_left_h,  upper_right_h ] ] )
            QX = np.asarray( [ [lower_left_qx, lower_right_qx], [upper_left_qx, upper_right_qx] ] )
            QY = np.asarray( [ [lower_left_qy, lower_right_qy], [upper_left_qy, upper_right_qy] ] )
            Z  = np.asarray( [ [lower_left_z,  lower_right_z ], [upper_left_z,  upper_right_z ] ] )
            
            if   quantity == 'h':
                S = H
            elif quantity == "eta":
                S = H + Z
            elif quantity == "qx":
                S = QX
            elif quantity == "qy":
                S = QY
            elif quantity == 'z':
                S = Z
            else:
                EXIT_HELP()
            
            self.ax.plot_surface(X, Y, S, color="#599DEE", rcount=1, ccount=1, shade=False, edgecolors='k', linewidth=0.25)
            
        elev = 29   if quantity != 'h' else 52
        azim = -120 if quantity != 'h' else 40
        
        self.ax.view_init(elev, azim)
        plt.savefig(os.path.join(self.savepath, "planar-soln-" + str(self.interval) + ".svg"), bbox_inches="tight")

def plot_surface(
    X, 
    Y, 
    Z, 
    zlabel, 
    test_number, 
    path, 
    quantity, 
    test_name
):
    fig, ax = plt.subplots( subplot_kw={"projection" : "3d"} )
    
    ax.plot_surface(X, Y, Z)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel(zlabel)
    
    filename = str(test_number) + "-surf-" + quantity + "-" + test_name
    
    plt.show()

    plt.savefig(os.path.join(path, filename), bbox_inches="tight")

    plt.clf()

def plot_contours(
    X, 
    Y, 
    Z, 
    ylabel, 
    test_number, 
    path, 
    quantity, 
    test_name
):
    fig, ax = plt.subplots()
    
    contourset = ax.contourf(X, Y, Z)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    
    colorbar = fig.colorbar(contourset)
    colorbar.ax.set_ylabel(ylabel)
    
    filename = str(test_number) + "-cont-" + quantity + "-" + test_name

    plt.savefig(os.path.join(path, filename), bbox_inches="tight")
    
    plt.clf()

class RowMajorSolution:
    def __init__(
        self, 
        mode
    ):
        if mode != "debug" and mode != "release":
            EXIT_HELP()
        
        self.savepath = set_path(mode)
        
        print("Searching for RowMajorSolution data in path", self.savepath)
        
        h_file  = "depths.csv"
        qx_file = "discharge_x.csv"
        qy_file = "discharge_y.csv"
        z_file  = "topo.csv"
        
        # finest reRowMajorSolution mesh info
        mesh_info_file = "mesh_info.csv"
        
        mesh_info = pd.read_csv( os.path.join(self.savepath, mesh_info_file) )
        
        # to access a dataframe with only one row
        # we use iloc, which stands for 'integer location'
        mesh_dim = int(mesh_info.iloc[0][r"mesh_dim"])
        xsz      = int(mesh_info.iloc[0][r"xsz"])
        ysz      = int(mesh_info.iloc[0][r"ysz"])
        
        xmin = mesh_info.iloc[0]["xmin"]
        xmax = mesh_info.iloc[0]["xmax"]
        ymin = mesh_info.iloc[0]["ymin"]
        ymax = mesh_info.iloc[0]["ymax"]
        
        x_dim = xmax - xmin
        y_dim = ymax - ymin
        
        N_x = 1
        N_y = 1
        
        if (xsz >= ysz):
            N_x = xsz / ysz
        else:
            N_y = ysz / xsz
        
        x = np.linspace(xmin, xmax, xsz)
        y = np.linspace(ymin, ymax, ysz)
        
        self.X, self.Y = np.meshgrid(x, y)
        
        self.h  = pd.read_csv( os.path.join(self.savepath, h_file ) )["results"].values.reshape(mesh_dim, mesh_dim)[0:ysz, 0:xsz]
        self.qx = pd.read_csv( os.path.join(self.savepath, qx_file) )["results"].values.reshape(mesh_dim, mesh_dim)[0:ysz, 0:xsz]
        self.qy = pd.read_csv( os.path.join(self.savepath, qy_file) )["results"].values.reshape(mesh_dim, mesh_dim)[0:ysz, 0:xsz]
        self.z  = pd.read_csv( os.path.join(self.savepath, z_file ) )["results"].values.reshape(mesh_dim, mesh_dim)[0:ysz, 0:xsz]

    def plot_surfaces(
        self, 
        test_number=0, 
        test_name="ad-hoc"
    ):
        print("Plotting flow RowMajorSolution and topography for test %s..." % test_name)

        plot_surface(self.X, self.Y, self.h,  "$\eta \, (m)$",        test_number, self.savepath, "eta", test_name)
        plot_surface(self.X, self.Y, self.qx, "$q_x \, (m^2s^{-1})$", test_number, self.savepath, "qx",  test_name)
        plot_surface(self.X, self.Y, self.qy, "$q_y \, (m^2s^{-1})$", test_number, self.savepath, "qy",  test_name)

    def plot_contours(
        self, 
        test_number=0, 
        test_name="ad-hoc"
    ):
        print("Plotting flow RowMajorSolution and topography for test %s..." % test_name)
        
        plot_contours(self.X, self.Y, self.h,  "$h  \, (m)$",          test_number, self.savepath, "h",  test_name)
        plot_contours(self.X, self.Y, self.qx, "$q_x \, (m^2s^{-1})$", test_number, self.savepath, "qx", test_name)
        plot_contours(self.X, self.Y, self.qy, "$q_y \, (m^2s^{-1})$", test_number, self.savepath, "qy", test_name)
        plot_contours(self.X, self.Y, self.z,  "$z  \, (m)$",          test_number, self.savepath, "z",  test_name)
        
    def plot_soln(
        self, 
        test_number=0,
        test_name="ad-hoc",
        plot_type="cont"
    ):
        if plot_type == "cont":
            self.plot_contours(test_number, test_name)
        elif plot_type == "surf":
            self.plot_surfaces(test_number, test_name)
        else:
            EXIT_HELP()
        
class DischargeErrors:
    def __init__(
        self, 
        solver, 
        mode
    ):
        if solver != "hw" and solver != "mw":
            EXIT_HELP()
        
        if mode != "debug" and mode != "release":
            EXIT_HELP()
        
        self.solver = solver;
    
        self.savepath = set_path(mode)
        
        print("Searching for discharge error data in path", self.savepath)
        
        sim_time_file = "clock_time_vs_sim_time.csv"
        qx0_file      = "qx0-c-prop.csv"
        qx1x_file     = "qx1x-c-prop.csv"
        qx1y_file     = "qx1y-c-prop.csv"
        qy0_file      = "qy0-c-prop.csv"
        qy1x_file     = "qy1x-c-prop.csv"
        qy1y_file     = "qy1y-c-prop.csv"
        
        self.sim_time = pd.read_csv( os.path.join(self.savepath, sim_time_file) )
        qx0           = pd.read_csv( os.path.join(self.savepath, qx0_file),  header=None )
        qx1x          = pd.read_csv( os.path.join(self.savepath, qx1x_file), header=None ) if solver == "mw" else None
        qx1y          = pd.read_csv( os.path.join(self.savepath, qx1y_file), header=None ) if solver == "mw" else None
        qy0           = pd.read_csv( os.path.join(self.savepath, qy0_file),  header=None )
        qy1x          = pd.read_csv( os.path.join(self.savepath, qy1x_file), header=None ) if solver == "mw" else None
        qy1y          = pd.read_csv( os.path.join(self.savepath, qy1y_file), header=None ) if solver == "mw" else None
        
        self.qx0_max  = qx0.abs().max(axis=1)
        self.qx1x_max = qx1x.abs().max(axis=1) if solver == "mw" else None
        self.qx1y_max = qx1y.abs().max(axis=1) if solver == "mw" else None
        self.qy0_max  = qy0.abs().max(axis=1)
        self.qy1x_max = qy1x.abs().max(axis=1) if solver == "mw" else None
        self.qy1y_max = qy1y.abs().max(axis=1) if solver == "mw" else None

    def plot_errors(
        self, 
        test_number=0, 
        test_name="ad-hoc"
    ):

        print("Plotting maximum discharge errors for test %s..." % test_name)

        plt.figure()
        
        plt.scatter(self.sim_time["sim_time"], self.qx0_max,  label='$q^0_x$', marker='x')
        plt.scatter(self.sim_time["sim_time"], self.qy0_max,  label='$q^0_y$', marker='x')
        
        if self.solver == "mw":
            plt.scatter(self.sim_time["sim_time"], self.qx1x_max, label='$q^{1x}_x$', marker='x')
            plt.scatter(self.sim_time["sim_time"], self.qx1y_max, label='$q^{1y}_x$', marker='x')
            plt.scatter(self.sim_time["sim_time"], self.qy1x_max, label='$q^{1x}_y$', marker='x')
            plt.scatter(self.sim_time["sim_time"], self.qy1y_max, label='$q^{1y}_y$', marker='x')
        
        xlim = ( self.sim_time["sim_time"].iloc[0], self.sim_time["sim_time"].iloc[-1] )

        plt.ticklabel_format(axis='x', style="sci")
        plt.xlim(xlim)
        plt.yscale("log")
        plt.legend()
        plt.ylabel("Maximum error")
        plt.xlabel("Simulation time (s)")

        filename = str(test_number) + "-c-prop-" + test_name

        plt.savefig(os.path.join(self.savepath, filename), bbox_inches="tight")
        
        plt.clf()

class Test:
    def __init__(
        self,
        test_case, 
        max_ref_lvl, 
        epsilon, 
        massint, 
        test_name, 
        solver, 
        c_prop_tests, 
        results, 
        input_file,
        mode
    ):
        if solver != "hw" and solver != "mw":
            EXIT_HELP()
        
        if mode != "debug" and mode != "release":
            EXIT_HELP()
        
        self.test_case   = test_case
        self.max_ref_lvl = max_ref_lvl
        self.epsilon     = epsilon
        self.massint     = massint 
        self.test_name   = test_name
        self.solver      = solver

        if self.test_case in c_prop_tests:
            self.row_major = "off"
            self.vtk       = "off"
            self.c_prop    = "on"
        else:
            self.row_major = "on"
            self.vtk       = "on"
            self.c_prop    = "off"

        self.results    = results
        self.input_file = input_file
        self.mode       = mode

    def set_params(
        self
    ):
        params = ("" +
            "test_case   %s\n" +
            "max_ref_lvl	%s\n" +
            "min_dt		1\n" +
            "respath	    %s\n" +
            "epsilon	    %s\n" +
            "tol_h		1e-3\n" +
            "tol_q		0\n" +
            "tol_s		1e-9\n" +
            "g			9.80665\n" +
            "massint		%s\n" +
            "solver		%s\n" +
            "wall_height	0\n" +
            "row_major    %s\n" +
            "c_prop %s\n" +
            "vtk        %s") % (
                self.test_case, 
                self.max_ref_lvl, 
                self.results, 
                self.epsilon, 
                self.massint, 
                self.solver, 
                self.row_major, 
                self.c_prop, 
                self.vtk
            )

        with open(self.input_file, 'w') as fp:
            fp.write(params)

    def run_test(
        self,
        solver_file
    ):
        self.set_params()

        subprocess.run( [solver_file, self.input_file] )

        if self.c_prop == "on":
            DischargeErrors(self.solver, self.mode).plot_errors(self.test_case, self.test_name)
        else:
            RowMajorSolution(self.mode).plot_soln(self.test_case, self.test_name)

def run_tests():
    if len(sys.argv) > 5:
        dummy, action, mode, solver, epsilon, max_ref_lvl = sys.argv
    
        if   mode == "debug":
            path = os.path.join("..", "out", "build", "x64-Debug")
        elif mode == "release":
            path = os.path.join("..", "out", "build", "x64-Release")
        else:
            EXIT_HELP()
            
        if solver != "hw" and solver != "mw":
            EXIT_HELP()
    else:
        EXIT_HELP()

    input_file  = os.path.join(path, "test", "inputs.par")
    solver_file = os.path.join(path, "gpu-mwdg2.exe")
    results     = os.path.join(path, "test", "results")
    
    test_names = [
        "1D-c-prop-x-dir-wet",
        "1D-c-prop-y-dir-wet",
        "1D-c-prop-x-dir-wet-dry",
        "1D-c-prop-y-dir-wet-dry",
        "wet-dam-break-x-dir",
        "wet-dam-break-y-dir",
        "dry-dam-break-x-dir",
        "dry-dam-break-y-dir",
        "dry-dam-break-w-fric-x-dir",
        "dry-dam-break-w-fric-y-dir",
        "wet-building-overtopping-x-dir",
        "wet-building-overtopping-y-dir",
        "dry-building-overtopping-x-dir",
        "dry-building-overtopping-y-dir",
        "triangular-dam-break-x-dir",
        "triangular-dam-break-y-dir",
        "parabolic-bowl-x-dir",
        "parabolic-bowl-y-dir",
        "three-cones",
        "differentiable-blocks",
        "non-differentiable-blocks",
        "radial-dam-break"
    ]
    
    massints = [
        1,     # 1D c prop x dir
        1,     # 1D c prop y dir
        1,     # 1D c prop x dir
        1,     # 1D c prop y dir
        2.5,   # wet dam break x dir
        2.5,   # wet dam break y dir
        1.3,   # dry dam break x dir
        1.3,   # dry dam break y dir
        1.3,   # dry dam break wh fric x dir
        1.3,   # dry dam break wh fric y dir
        10,    # wet building overtopping x dir
        10,    # wet building overtopping y dir
        10,    # dry building overtopping x dir
        10,    # dry building overtopping y dir
        29.6,  # triangular dam break x dir
        29.6,  # triangular dam break y dir
        108,  # parabolic bowl x dir
        108,  # parabolic bowl y dir
        1,     # three cones
        1,     # differentiable blocks
        1,     # non-differentiable blocks
        3.5    # radial dam break
    ]
    
    tests = []
    
    with open("tests.txt", 'r') as fp:
        tests = fp.readlines()
        tests = [int( test.rstrip() ) for test in tests]
    
    c_prop_tests = [1, 2, 3, 4, 19, 20, 21]
    
    for test in tests:
        Test(
            test,
            max_ref_lvl,
            epsilon,
            massints[test - 1],
            test_names[test - 1],
            solver,
            c_prop_tests,
            results,
            input_file,
            mode
        ).run_test(solver_file)

def plot_soln_planar():
    if len(sys.argv) > 5:
        dummy, action, mode, solver, testdir, quantity, interval = sys.argv
        
        PlanarSolution(mode, solver, interval, testdir).plot_soln(quantity)
    else:
        EXIT_HELP()

def plot_soln_row_major():
    if len(sys.argv) > 3:
        dummy, action, mode, plot_type = sys.argv
        
        RowMajorSolution(mode).plot_soln(plot_type)
    else:
        EXIT_HELP()

def plot_c_prop():
    if len(sys.argv) > 3:
        dummy, action, mode, solver = sys.argv
        
        DischargeErrors(solver, mode).plot_errors()
    else:
        EXIT_HELP()

# from: https://stackoverflow.com/questions/12444716/how-do-i-set-the-figure-title-and-axes-labels-font-size-in-matplotlib
params = {
    "legend.fontsize" : "xx-large",
    "axes.labelsize"  : "xx-large",
    "axes.titlesize"  : "xx-large",
    "xtick.labelsize" : "xx-large",
    "ytick.labelsize" : "xx-large"
}

pylab.rcParams.update(params)

action = sys.argv[1]

if   action == "run":
    run_tests()
elif action == "planar":
    plot_soln_planar()
elif action == "row_major":
    plot_soln_row_major()
elif action == "c_prop":
    plot_c_prop()
else:
    EXIT_HELP()