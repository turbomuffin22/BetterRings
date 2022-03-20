from polycircles import polycircles
import os, sys, subprocess
import geopy.distance
import simplekml
import geopy

# Example Site
# siteName : Portnoff
# lattitude: 35.646015
# longitude: -120.738757

def main():
    configuration = {
        "lattitude": float(input('Site lattitude: ')),
        "longitude": float(input('Site longitude: ')),
        "siteName": input("Site name: "),
        "kml": simplekml.Kml(),
        "horns": [
            { "beamWidth": 0, "distance": 0.155, "model": "Terragraph DN" },
            { "beamWidth": 360, "distance": 10.0, "model": "Omni" },
            { "beamWidth": 13, "distance": 7.0, "model": "UltraHorn" },
            { "beamWidth": 20, "distance": 6.0, "model": "AH20" },
            { "beamWidth": 30, "distance": 5.0, "model": "AH30" },
            { "beamWidth": 60, "distance": 2.5, "model": "AH60" },
            { "beamWidth": 90, "distance": 1.5, "model": "AH90" },
        ]
    }

    while True:
        promptForHornSelection(configuration)
        generatePolygon(configuration)
        saveKML(configuration)
        configuration["kml"] = simplekml.Kml()


def promptForHornSelection(configuration):
    for i, horn in enumerate(configuration["horns"]):
        print(f'{i + 1}={horn["beamWidth"]}° - {horn["distance"]} Miles')
    print("0=EXIT")

    configuration["selectedHorn"] = int(input("Select Horn Type: "))
    if horn == 0: exit()

    selectedHorn = configuration["selectedHorn"]
    horns = configuration["horns"]
    if horns[selectedHorn - 1]["beamWidth"] in [0, 360]:
        return

    configuration["selectedAzimuth"] = int(input("Desired Azimuth: "))

def generatePolygon(configuration):
    selectedHorn = configuration["selectedHorn"]
    horns = configuration["horns"]

    if horns[selectedHorn - 1]["beamWidth"] == 360:
        handleOmni(configuration)
    elif horns[selectedHorn - 1]["beamWidth"] == 0:
        for i in [0, 90, 180, 270]:
            configuration["selectedAzimuth"] = i
            handlePolygon(configuration)
    else:
        handlePolygon(configuration)

def handlePolygon(configuration):
    selectedHorn = configuration["selectedHorn"]
    horns = configuration["horns"]

    beamwidth = horns[selectedHorn - 1]["beamWidth"]
    if horns[selectedHorn - 1]["beamWidth"] == 0:
        beamwidth = 90

    azimuth = (configuration["selectedAzimuth"] - (beamwidth / 2)) % 360
    start = geopy.Point(configuration["lattitude"], configuration["longitude"])
    distance = horns[selectedHorn - 1]["distance"]
    d = geopy.distance.distance(miles=distance)
    final = d.destination(point=start, bearing=azimuth)

    hornCanopy = [(configuration["longitude"], configuration["lattitude"])]

    for i in range(0, (beamwidth + 1) % 360):
        hornCanopy.append((final[1], final[0]))
        distance += 1
        azimuth += 1
        final = d.destination(point=start, bearing=azimuth)

    hornCanopy.append((configuration["longitude"], configuration["lattitude"]))

    configuration["polygon"] = configuration["kml"].newpolygon(tessellate=1)
    configuration["polygon"].style.polystyle.color = getColorForDistance(horns[selectedHorn - 1]["distance"])
    configuration["polygon"].outerboundaryis.coords = hornCanopy
    return

def handleOmni(configuration):
    selectedHorn = configuration["selectedHorn"]
    horns = configuration["horns"]

    polycircle = polycircles.Polycircle(
            latitude=configuration["lattitude"],
            longitude=configuration["longitude"],
            radius=horns[selectedHorn - 1]["distance"] * 1609, # Requires meters
            number_of_vertices=36
        )
    configuration["polygon"] = configuration["kml"].newpolygon(tessellate=1)
    configuration["polygon"].style.polystyle.color = getColorForDistance(horns[selectedHorn - 1]["distance"])
    configuration["polygon"].outerboundaryis = polycircle.to_kml()

def saveKML(configuration):
    if "selectedAzimuth" in configuration:
        filePath = (f'{configuration["siteName"]}-{configuration["horns"][configuration["selectedHorn"] - 1]["model"]}-{configuration["selectedAzimuth"]}Az.kml')
    else:
        filePath = (f'{configuration["siteName"]}-{configuration["horns"][configuration["selectedHorn"] - 1]["model"]}.kml')
    configuration["kml"].save(filePath)

    if sys.platform == "win32":
        os.startfile(filePath, 'open')
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filePath])

def getColorForDistance(distance):
    if distance >= 7: return "50FF7800" #Orange
    if distance >= 6: return "5000FF14" #Green
    if distance >= 5: return "5014F0FF" #Teal
    if distance >= 2.5: return "501478FF" #Blue
    return "7500FF14"   #"501400FF" #Red

if __name__ == '__main__':
    main()
