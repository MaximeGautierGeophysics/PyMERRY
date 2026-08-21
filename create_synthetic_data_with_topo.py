#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 12:14:50 2026

@author: Maxime GAUTIER
"""


# %% IMPORT:
import os
import numpy as np
import pygimli as pg
import pandas as pd
import matplotlib.pyplot as plt
import tools.PyMERRY as PM

np.random.seed(42)

# %% CREATE DOMAIN WITH TOPOGRAPHY:
# Create an random sinusoidal toography:
topo = [[xi, 0.5*np.cos(xi) + 1 + np.random.uniform(-0.2, 0.2)]
        for xi in np.arange(-29, 29, 0.5)]

# Prepare electrode positions incluting topography: -15 to 15 m, 21 electrodes:
x = np.linspace(-15, 15, 21)
y = np.interp(x, [p[0] for p in topo], [p[1] for p in topo])
electrodes_positions = np.array(np.vstack((x, y)).T)

# Merge sort and del double of points coordintates from topo and electrodes:
points = sorted({p[0]: p for p in topo + [[xi, yi]
                                          for xi, yi in zip(x, y)]}.values())

# Round values:
topo = np.round(topo, 3).tolist()
x = np.round(x, 3)
y = np.round(y, 3)
electrodes_positions = np.round(electrodes_positions, 3)
points = np.round(points, 3).tolist()

# Geometries: layers and bodies:
# Points:
A = [-30, 0]
B = [30, 0]
C = [30, -1]
D = [30, -5]
E = [30, -15]
F = [-30, -15]
G = [-30, -5]
H = [-30, -1]

layer_1 = pg.meshtools.createPolygon([A, *points, B, C, H], isClosed=True,
                                     marker=1)

layer_2 = pg.meshtools.createPolygon([H, C, D, G], bisClosed=True, marker=2)

layer_3 = pg.meshtools.createPolygon([G, D, E, F], isClosed=True, marker=3)

body_1 = pg.meshtools.createCircle(pos=[-5, -3.], radius=[4, 1], marker=4,
                                   boundaryMarker=10, area=0.1)

body_2 = pg.meshtools.createPolygon([(1, -4), (2, -1.5), (4, -2), (5, -2),
                                    (8, -3), (5, -3.5), (3, -4.5)],
                                    isClosed=True, addNodes=3,
                                    interpolate="spline", marker=5)

# Merge elements:
domain_direct = layer_1 + layer_2 + layer_3 + body_1 + body_2


# Create nodes and boundaries:
# Nodes:
nA = domain_direct.node(domain_direct.findNearestNode(A))
nB = domain_direct.node(domain_direct.findNearestNode(B))
nC = domain_direct.node(domain_direct.findNearestNode(C))
nD = domain_direct.node(domain_direct.findNearestNode(D))
nE = domain_direct.node(domain_direct.findNearestNode(E))
nF = domain_direct.node(domain_direct.findNearestNode(F))
nG = domain_direct.node(domain_direct.findNearestNode(G))
nH = domain_direct.node(domain_direct.findNearestNode(H))

topo_nodes = [domain_direct.node(domain_direct.findNearestNode(pi))
              for pi in [A, *points, B]]

body_1_nodes = [[b.nodes()[0].x(), b.nodes()[0].y()]
                for b in body_1.boundaries()]
body_1_nodes = [domain_direct.node(domain_direct.findNearestNode(pi))
                for pi in [*body_1_nodes, body_1_nodes[0]]]

body_2_nodes = [[b.nodes()[0].x(), b.nodes()[0].y()]
                for b in body_2.boundaries()]
body_2_nodes = [domain_direct.node(domain_direct.findNearestNode(pi))
                for pi in [*body_2_nodes, body_2_nodes[0]]]


# Topographic boundary:
[domain_direct.createEdge(topo_nodes[i-1], topo_nodes[i], marker=-1)
 for i in range(1, len(topo_nodes))]

# Box boundary:
domain_direct.createEdge(nB, nC, marker=-2)
domain_direct.createEdge(nC, nD, marker=-2)
domain_direct.createEdge(nD, nE, marker=-2)
domain_direct.createEdge(nE, nF, marker=-2)
domain_direct.createEdge(nF, nG, marker=-2)
domain_direct.createEdge(nG, nH, marker=-2)
domain_direct.createEdge(nH, nA, marker=-2)

# Layers boundary:
domain_direct.createEdge(nH, nC, marker=1)
domain_direct.createEdge(nG, nD, marker=2)

# Bodies' boundaries:
[domain_direct.createEdge(body_1_nodes[i-1], body_1_nodes[i], marker=3)
 for i in range(1, len(body_1_nodes))]
[domain_direct.createEdge(body_2_nodes[i-1], body_2_nodes[i], marker=4)
 for i in range(1, len(body_2_nodes))]

# Mesh refinement near electrodes:
for xi, yi in zip(x, y):
    domain_direct.createNode(pg.Vector([xi, yi]) - [0, 0.1])

# Create a mesh:
mesh_direct = pg.meshtools.createMesh(domain_direct, quality=34, area=0.25)

# Correct layer 2 marker (reset to 0 while elements merging):
[c.setMarker(2) for c in mesh_direct.cells() if c.marker() == 0]

# %% CREATE MESH FOR INVERSION:
# Domain:
inv_box = pg.meshtools.createPolygon([A, *points, B, E, F], isClosed=True,
                                     marker=1)
# Topographic boundary:
topo_nodes = [inv_box.node(inv_box.findNearestNode(pi))
              for pi in [A, *points, B]]

[inv_box.createEdge(topo_nodes[i-1], topo_nodes[i], marker=-1)
 for i in range(1, len(topo_nodes))]

# Box boundary:
nA = inv_box.node(inv_box.findNearestNode(A))
nB = inv_box.node(inv_box.findNearestNode(B))
nE = inv_box.node(inv_box.findNearestNode(E))
nF = inv_box.node(inv_box.findNearestNode(F))

inv_box.createEdge(nB, nE, marker=-2)
inv_box.createEdge(nE, nF, marker=-2)
inv_box.createEdge(nF, nA, marker=-2)

# Mesh refinement near electrodes:
for xi, yi in zip(x, y):
    inv_box.createNode(pg.Vector([xi, yi]) - [0, 0.1])

# Create a mesh:
mesh = pg.meshtools.createMesh(inv_box, quality=34, area=0.25)

# Extend mesh for avoid egde effects:
inv_mesh = pg.meshtools.appendTriangleBoundary(mesh=mesh, xbound=30, ybound=15,
                                               marker=0)


# %% DEFINE TRUE MODEL:
markers = np.array([c.marker() for c in mesh_direct.cells()])
true_model = np.zeros((markers.shape[0], ))
true_model[markers == 1] = 100
true_model[markers == 2] = 75
true_model[markers == 3] = 50
true_model[markers == 4] = 150
true_model[markers == 5] = 25


# %% GENERATE SYNTHETIC DATA:
# Create survey with dipole-dipole acquisition scheme:
survey = pg.physics.ert.createData(elecs=electrodes_positions, schemeName='dd')

# compute geometrical factors considering topography:
survey["k"] = pg.physics.ert.createGeometricFactors(survey, mesh=mesh_direct,
                                                    numerical=True)

# Gerenate synthetic data:
survey = pg.physics.ert.simulate(mesh_direct, scheme=survey, res=true_model)

# Generate random gaussian noise:
rhoa = np.array(survey["rhoa"])
noise_level = np.random.normal(0, 0.01, len(rhoa))
rhoa_noise = rhoa * (1 + noise_level)
noise = np.abs(rhoa-rhoa_noise) / rhoa
survey["rhoa"] = rhoa_noise
survey["err"] = noise
survey["valid"] = 1


# %% INVERT DATA:
mgr = pg.physics.ert.ERTManager()
mgr.setData(survey)
mgr.invert(mesh=inv_mesh, lam=20, verbose=True)

model = np.array(mgr.model)


# %% EXPORT:
os.makedirs(os.path.join("input_data_with_topo"),
                          exist_ok=True)

# Data file:
survey.save(os.path.join("input_data_with_topo", "ert_data.dat"))

# Model file:
np.savetxt(os.path.join("input_data_with_topo", "model.txt"),
           np.array([[c.id(), mi] for c, mi in zip(mesh.cells(), model)]),
           delimiter=";", fmt=["%d", "%.6f"])

# Mesh:
nodes_table, cells_table, = PM.InputTools.mesh_tables(mesh)
np.savetxt(os.path.join("input_data_with_topo", "mesh_cells_table.txt"),
           cells_table, delimiter=";", fmt=["%d", "%d", "%d", "%d"])
np.savetxt(os.path.join("input_data_with_topo", "mesh_nodes_table.txt"),
           nodes_table, delimiter=";", fmt=["%d", "%.6f", "%.6f", "%.6f"])
# %% PLOTS:
# Plot direct mesh:
fig, ax = plt.subplots()
ax, cb = pg.show(mesh_direct, showMesh=True, ax=ax, markers=True,
                 orientation="vertical", label="Markers")
ax.scatter(x, y, marker="v", color="black", label="Electrodes")
ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.legend(loc="lower right")
ax.set_title(str(mesh_direct), loc="left")

# Plot true model:
fig, ax = plt.subplots()
ax, cb = pg.show(mesh_direct, true_model, ax=ax, cMap="Spectral_r",
                 logScale=False, cMin=25, cMax=150, orientation="vertical",
                 label="Electrical resistivity " + r"$\rho{}\;(\Omega{}.m)$")

ax.scatter(x, y, marker="v", color="black", label="Electrodes")
ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.legend(loc="lower right")
ax.set_title("True resistivity model", loc="left")

# Plot parametric mesh:
fig, ax = plt.subplots()
ax, cb = pg.show(mesh, showMesh=True, ax=ax, markers=True,
                 orientation="vertical", label="Markers")
ax.scatter(x, y, marker="v", color="black", label="Electrodes")
ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.legend(loc="lower right")
ax.set_title("Parametric mesh " + str(mesh), loc="left")

# Plot inversion mesh enlarged:
fig, ax = plt.subplots()
ax, cb = pg.show(inv_mesh, showMesh=True, ax=ax, markers=True,
                 orientation="vertical", label="Markers")
ax.scatter(x, y, marker="v", color="black", label="Electrodes")
ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.legend(loc="lower right")
ax.set_title("Inversion mesh " + str(mesh), loc="left")

# Plot synthetic data:
fig, ax = plt.subplots()
ax, cb = pg.show(survey, ax=ax, cMap="Spectral_r",
                 logScale=False, cMin=25, cMax=150, orientation="vertical",
                 label="Apparent resistivity " + r"$\rho{}_{a}\;(\Omega{}.m)$")
ax.set_xlabel("x (m)")
ax.set_ylabel("Measurement level")


# Plot true model:
fig, ax = plt.subplots()
ax, cb = pg.show(mesh, model, ax=ax, cMap="Spectral_r",
                 logScale=False, cMin=25, cMax=150, orientation="vertical",
                 label="Electrical resistivity " + r"$\rho{}\;(\Omega{}.m)$")

ax.scatter(x, y, marker="v", color="black", label="Electrodes")
ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.legend(loc="lower right")
ax.set_title("Model", loc="left")
