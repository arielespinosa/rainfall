#!/usr/bin/python
#--------------------------------------------------------------------------------------
# Convertidor de netcdf4 a Ascii para las salidas del modelo WRF.
#--------------------------------------------------------------------------------------

# Importing NetCDF LIB

from  scipy.io import netcdf
# Importing Python and System LIBS
import numpy as np
import sys, os, shutil, glob
import string
#import matplotlib.pyplot as plt

print ""
print "----------------------------------------------------------"
print " Converting WRF outs in NETCDF format to Ascii format ..."
print "----------------------------------------------------------"

# Open input file

inputfile = sys.argv[1]
outputdir = sys.argv[2]

print ""
print "Input file name = ", inputfile

ncFile =netcdf.netcdf_file(inputfile, 'r')
inputfile = inputfile[-30:]

# Splitting names

name1 = inputfile[0:24]
name2 = ".00.00"

inputfile = name1 + name2
#inputfile=string.replace(inputfile,'wrfout_d01','wrfout_d03')

# Reading info from input file

print ""
print "Reading info about input file ..."

# Dimensions of domain
nx =  ncFile.dimensions['west_east']
ny =  ncFile.dimensions['south_north']
nz =  ncFile.dimensions['bottom_top']
nzsoil =  ncFile.dimensions['soil_layers_stag']

# Get the grid spacing
dx = float(ncFile.DX)
dy = float(ncFile.DY)

cen_lat = float(ncFile.CEN_LAT)
cen_lon = float(ncFile.CEN_LON)
truelat1 = float(ncFile.TRUELAT1)
truelat2 = float(ncFile.TRUELAT2)
standlon = float(ncFile.STAND_LON)
proj = ncFile.MAP_PROJ
#proj_text = ncFile.MAP_PROJ_CHAR

# Get date and hour form input file
date = ncFile.START_DATE

print "Description"
print "NX = ",nx," NY = ",ny," NZ = ",nz," NZ_SOIL = ",nzsoil," DX = ",dx," Time = ",date

# Flags
os.system("touch " + outputdir + "/." + inputfile + ".flag_d03")


# ----------------------------------------------------------------
# Procesing vars from input file
# ----------------------------------------------------------------

# Procesing rain field

rainArrayC =  ncFile.variables['RAINC'][:]
rainArrayNC =  ncFile.variables['RAINNC'][:]

rainArray = rainArrayC + rainArrayNC

print ""
print "Procesing rain field (mm/3h)..."
print "min = ", np.min(rainArray), "max = ", np.max(rainArray)

# Ver para cuando sea mayor de 3 horas el rango de pronostico

rainArray.shape  = (ny, nx)
rainArray = rainArray[-1::-1,:]

np.savetxt(outputdir + "/rain." + inputfile + ".txt", rainArray, fmt="%7.3f")

# ----------------------------------------------------------------
# Procesing temperature at 2 meters field

tempK =  ncFile.variables['T2'][:]

tempC = tempK - 273.15

print ""
print "Procesing temperature at 2 m field (C)..."
print "min = ", np.min(tempC), "max = ", np.max(tempC)

tempC.shape  = (ny, nx)
tempC = tempC[-1::-1,:]

np.savetxt(outputdir + "/temp2m." + inputfile + ".txt", tempC, fmt="%7.3f")


# ----------------------------------------------------------------
# Procesing global radiation field

radg =  ncFile.variables['SWDOWN'][:]


print ""
print "Procesing global radiation field (W m-2)..."
print "min = ", np.min(radg), "max = ", np.max(radg)

radg.shape  = (ny, nx)
radg = radg[-1::-1,:]

np.savetxt(outputdir + "/rad_glob." + inputfile + ".txt", radg, fmt="%7.3f")



# ----------------------------------------------------------------
# Procesing mean sea level presion field

hgt =  ncFile.variables['HGT'][:]
presPa =  ncFile.variables['PSFC'][:]
temps =  ncFile.variables['T2'][:]

stemps = temps+6.5*hgt/1000.
mslp = presPa*np.exp(9.81/(287.0*stemps)*hgt)*0.01 + (6.7 * hgt / 1000)


print ""
print "Procesing mean sea level presion field (hPa)..."
print "min = ", np.min(mslp), "max = ", np.max(mslp)

mslp.shape  = (ny, nx)
mslp = mslp[-1::-1,:]

np.savetxt(outputdir + "/mslp." + inputfile + ".txt", mslp, fmt="%7.3f")

# ----------------------------------------------------------------
# Procesing wind at 10 meters field

u10m =  ncFile.variables['U10'][:]
v10m =  ncFile.variables['V10'][:]

windu = u10m*u10m
windv = v10m*v10m

# Speed
windspeed = 3.6*(windu+windv)**0.5

print ""
print "Procesing wind speed field (km/h) ..."
print "min = ", np.min(windspeed), "max = ", np.max(windspeed)

windspeed.shape  = (ny, nx)
windspeed = windspeed[-1::-1,:]

np.savetxt(outputdir + "/wind_speed." + inputfile + ".txt", windspeed, fmt="%7.3f")

# U
print ""
print "Procesing U - wind speed field (km/h) ..."
print "min = ", np.min(u10m), "max = ", np.max(u10m)

u10m.shape  = (ny, nx)
u10m = u10m[-1::-1,:]

np.savetxt(outputdir + "/u10_speed." + inputfile + ".txt", u10m, fmt="%7.3f")

# V
print ""
print "Procesing V - wind speed field (km/h) ..."
print "min = ", np.min(v10m), "max = ", np.max(v10m)

v10m.shape  = (ny, nx)
v10m = v10m[-1::-1,:]

np.savetxt(outputdir + "/v10_speed." +  inputfile + ".txt", v10m, fmt="%7.3f")

## Direction
#winddir = 

#print ""
#print "Procesing wind direction field ..."
#print "min = ", np.min(winddir), "max = ", np.max(winddir)

#winddir.shape  = (ny, nx)
#np.savetxt(outputdir + "/wind_dir." + "_d03_" + inputfile + ".txt", winddir, fmt="%7.3f")

## ----------------------------------------------------------------
## Procesing relative humidity at 2 meters field

presPa =  ncFile.variables['PSFC'][:]
temps =  ncFile.variables['T2'][:]
qhum =  ncFile.variables['Q2'][:]

# Dew point temp
es = 6.112 * np.exp(17.67 * temps/(temps + 243.5))
w = qhum/(1-qhum)
e = (w * presPa / (.622 + w)) / 100
td2m = (243.5 * np.log(e/6.112))/(17.67-np.log(e/6.112))

# Temp Air
t2m = temps - 273.15

ens=6.1*10*(7.5*td2m/(237.7+td2m))
esa=6.1*10*(7.5*t2m/(237.7+t2m))
rh2m = 100. * (ens/esa)

print ""
print "Procesing relative humidity at 2 meters field (%)..."
print "min = ", np.min(rh2m), "max = ", np.max(rh2m)

rh2m.shape  = (ny, nx)
rh2m = rh2m[-1::-1,:]

np.savetxt(outputdir + "/rh2m." + inputfile + ".txt", rh2m, fmt="%7.3f")


# ----------------------------------------------------------------
# Procesing sfroff field

sfroff =  ncFile.variables['SFROFF'][:]

print ""
print "Procesing SFROFF field (mm)..."
print "min = ", np.min(sfroff), "max = ", np.max(sfroff)

# Ver para cuando sea mayor de 3 horas el rango de pronostico

sfroff.shape  = (ny, nx)
sfroff = sfroff[-1::-1,:]

np.savetxt(outputdir + "/sfroff." + inputfile + ".txt", sfroff, fmt="%7.3f")



# ----------------------------------------------------------------
# Procesing udroff field

udroff =  ncFile.variables['UDROFF'][:]

print ""
print "Procesing UDROFF field (mm)..."
print "min = ", np.min(udroff), "max = ", np.max(udroff)

# Ver para cuando sea mayor de 3 horas el rango de pronostico

udroff.shape  = (ny, nx)
udroff = udroff[-1::-1,:]

np.savetxt(outputdir + "/udroff." + inputfile + ".txt", udroff, fmt="%7.3f")



# ----------------------------------------------------------------
# Procesing CLDFRA field

icldfra =  ncFile.variables['CLDFRA'][:]

cldfra = np.zeros(shape=(ny,nx))
for i in range(nz):
	cldfra = cldfra + icldfra[0,i,:,:]


print ""
print "Procesing CLDFRA field (%)..."
print "min = ", np.min(cldfra), "max = ", np.max(cldfra)

# Ver para cuando sea mayor de 3 horas el rango de pronostico

cldfra.shape  = (ny, nx)
cldfra = cldfra[-1::-1,:]

np.savetxt(outputdir + "/cldfra." + inputfile + ".txt", cldfra, fmt="%7.3f")


# ----------------------------------------------------------------
# Procesing TSLB field

tsoil =  ncFile.variables['TSLB'][:]

lsoils = [5,10,30,70]
for i in range(nzsoil):

	print ""
	print "Procesing TSLB "+str(lsoils[i])+"cm field (C)..."
	print "min = ", np.min(tsoil[0,i,:,:]-273.15), "max = ", np.max(tsoil[0,i,:,:]-273.15)
	vtsoil = tsoil[0,i,:,:]-273.15
	# Ver para cuando sea mayor de 3 horas el rango de pronostico

	vtsoil.shape  = (ny, nx)
	vtsoil = vtsoil[-1::-1,:]

	np.savetxt(outputdir + "/tslb_"+str(lsoils[i])+"cm_." + inputfile + ".txt", vtsoil, fmt="%7.3f")



# ----------------------------------------------------------------
# Procesing SMOIS field

smois =  ncFile.variables['SMOIS'][:]

lsoils = [5,10,30,70]
for i in range(nzsoil):

	print ""
	print "Procesing SMOIS "+str(lsoils[i])+"cm field (C)..."
	print "min = ", np.min(smois[0, i, :, :]), "max = ", np.max(smois[0, i, :, :])
	vsmois = smois[0, i, :, :]
	# Ver para cuando sea mayor de 3 horas el rango de pronostico

	vsmois.shape  = (ny, nx)
	vsmois = vsmois[-1::-1,:]

	np.savetxt(outputdir + "/smois_"+str(lsoils[i])+"cm_." + inputfile + ".txt", vsmois, fmt="%7.3f")



# ----------------------------------------------------------------
# Procesing SH2O field

sh2o =  ncFile.variables['SH2O'][:]

lsoils = [5,10,30,70]
for i in range(nzsoil):

	print ""
	print "Procesing SH2O "+str(lsoils[i])+"cm field (C)..."
	print "min = ", np.min(sh2o[0, i, :, :]), "max = ", np.max(sh2o[0, i, :, :])
	vsh2o = sh2o[0, i, :, :]
	# Ver para cuando sea mayor de 3 horas el rango de pronostico

	vsh2o.shape  = (ny, nx)
	vsh2o = vsh2o[-1::-1,:]

	np.savetxt(outputdir + "/sh2o_"+str(lsoils[i])+"cm_." + inputfile + ".txt", vsh2o, fmt="%7.3f")



print ""
print "------------------------------------"
print " Finish"
print "------------------------------------"
print ""
