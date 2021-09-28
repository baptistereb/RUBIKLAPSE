# Created by Wayne Porter and modify by @baptistereb (on github)
# Cura plugin allowing to make 3d printing timelpase

from ..Script import Script


class RubikLapse(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Rubik Lapse",
            "key": "RubikLapse",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "trigger":
                {
                    "label": "GCODE PHOTO",
                    "description": "Envoyez un gcode pour effectuer la prise de vue",
                    "type": "bool",
                    "default_value": false
                },
                "trigger_command":
                {
                    "label": "GCODE PHOTO",
                    "description": "gcode a envoyer pour déclencher la photo",
                    "type": "str",
                    "default_value": "",
                    "enabled": "trigger"
                },
                "park_print_head":
                {
                    "label": "PARK",
                    "description": "Bouger le chariot à une position précise pour activer la photo",
                    "type": "bool",
                    "default_value": true
                },
                "head_park_y":
                {
                    "label": "POSITION Y PARK",
                    "description": "position de park y",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 235,
                    "enabled": "park_print_head"
                },
                "head_park_x":
                {
                    "label": "POSITION X PARK",
                    "description": "position de park x",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 235,
                    "enabled": "park_print_head"
                },
                "pause_length":
                {
                    "label": "PAUSE TIMING",
                    "description": "Combien de temps faut t-il attendre sans bouger à la position 1",
                    "type": "int",
                    "default_value": 2,
                    "minimum_value": 0,
                    "unit": "ms",
                    "enabled": "park_print_head"
                },
                "park_feed_rate":
                {
                    "label": "VITESSE DE MOUVEMENT",
                    "description": "A quel vitesse le chariot va se déplacer",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 60,
                    "enabled": "park_print_head"
                },
                "park_print_head2":
                {
                    "label": "PARK2",
                    "description": "Bouger le chariot à une position précise pour prendre la photo",
                    "type": "bool",
                    "default_value": false
                },
                "head_park_x2":
                {
                    "label": "POSITION X PARK2",
                    "description": "position de park2 x",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 230,
                    "enabled": "park_print_head2"
                },
                "head_park_y2":
                {
                    "label": "POSITION Y PARK2",
                    "description": "position de park2 y",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 235,
                    "enabled": "park_print_head2"
                },
                "pause_length2":
                {
                    "label": "PAUSE TIMING 2",
                    "description": "Combien de temps faut t-il attendre sans bouger à la position 2",
                    "type": "int",
                    "default_value": 3000,
                    "minimum_value": 0,
                    "unit": "ms",
                    "enabled": "park_print_head2"
                },
                "park_feed_rate2":
                {
                    "label": "VITESSE DE MOUVEMENT",
                    "description": "A quel vitesse le chariot va se déplacer",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 60,
                    "enabled": "park_print_head2"
                },
                "extrude":
                {
                    "label": "RECTRACTATION",
                    "description": "Souhaitez-vous retracter le filament",
                    "type": "bool",
                    "default_value": false
                },
                "extrud":
                {
                    "label": "LONGUEUR DE LA RECTRACTATION",
                    "description": "De combien de mm voulez-vous retractez le filament ?",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 7,
                    "enabled": "extrude"
                },
                "extrud_rapidity":
                {
                    "label": "VITESSE DE LA RECTRACTATION",
                    "description": "A quel vitesse vous souhaitez retractez le filament ?",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 60,
                    "enabled": "extrude"
                },
                "modifyz":
                {
                    "label": "MODIFIER Z",
                    "description": "Lever le charriot (en Z) afin que la buse ne touche pas la paroi en premier.",
                    "type": "bool",
                    "default_value": false
                },
                "zadd":
                {
                    "label": "VALEUR Z AJOUTE",
                    "description": "A combien faut il lever le charriot(en mm)",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 3,
                    "enabled": "modifyz"
                }
            }
        }"""

    def execute(self, data):
        modifyz = self.getSettingValueByKey("modifyz")
        zadd = self.getSettingValueByKey("zadd")
        trigger = self.getSettingValueByKey("trigger")
        feed_rate = self.getSettingValueByKey("park_feed_rate")*60
        feed_rate2 = self.getSettingValueByKey("park_feed_rate2")*60
        extrude = self.getSettingValueByKey("extrude")
        extrud = self.getSettingValueByKey("extrud")
        extrud2 = -1*extrud
        extrud_rapidity = self.getSettingValueByKey("extrud_rapidity")*60
        park_print_head = self.getSettingValueByKey("park_print_head")
        park_print_head2 = self.getSettingValueByKey("park_print_head2")
        x_park = self.getSettingValueByKey("head_park_x")
        x_park2 = self.getSettingValueByKey("head_park_x2")
        y_park = self.getSettingValueByKey("head_park_y")
        y_park2 = self.getSettingValueByKey("head_park_y2")
        trigger_command = self.getSettingValueByKey("trigger_command")
        pause_length = self.getSettingValueByKey("pause_length")
        pause_length2 = self.getSettingValueByKey("pause_length2")
        gcode_to_append = ""
        last_x = 0
        last_y = 0
        last_z = 0
        last_e = 0

        if park_print_head:
            gcode_to_append += self.putValue(G=1, F=feed_rate, X=x_park, Y=y_park) + " ;Park print head\n"
            gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"
            gcode_to_append += self.putValue(G=4, P=pause_length) + " ;Wait for camera\n"

        if park_print_head2:
            gcode_to_append += self.putValue(G=1, F=feed_rate2, X=x_park2, Y=y_park2) + " ;Park print head2\n"
            gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"
            gcode_to_append += self.putValue(G=4, P=pause_length2) + " ;Wait for camera\n"

        if trigger:
            gcode_to_append += trigger_command + " ;Snap Photo\n"

        for idx, layer in enumerate(data):
            for line in layer.split("\n"):
                if self.getValue(line, "G") in {0, 1}:  # Track X,Y,Z,E location.
                    last_x_recup = self.getValue(line, "X", last_x)
                    last_y_recup = self.getValue(line, "Y", last_y)
                    last_z_recup = self.getValue(line, "Z", last_z)
                    last_e_recup = self.getValue(line, "E", last_e)
                    if last_x_recup != 0:
                        last_x = last_x_recup
                    if last_y_recup != 0:
                        last_y = last_y_recup
                    if last_z_recup != 0:
                        last_z = last_z_recup
                    if last_e_recup != 0:
                        last_e = last_e_recup
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:

                    extrusion = last_e-extrud
                    z = last_z+zadd

                    layer += ";RubikLapse Begin\n"

                    if extrude:
                        layer += "G1 E%s F%s ;retract\n" % (extrusion, extrud_rapidity)
                        layer += "M400 ;attendre la fin du mouvement\n"

                    layer += gcode_to_append

                    if modifyz:
                        layer += "G0 X%s Y%s Z%s;retour pos d'origine + z\n" % (last_x, last_y, z)
                        layer += "M400 ;attendre la fin du mouvement\n"
                        layer += "G1 X%s Y%s Z%s E%s ;retour pos d'origine\n" % (last_x, last_y, last_z, last_e)
                    else:
                        layer += "G1 X%s Y%s E%s ;retour pos d'origine\n" % (last_x, last_y, last_e)

                    layer += "M400 ;attendre la fin du mouvement\n"

                    layer += ";RubikLapse End\n"

                    data[idx] = layer
                    break
        return data

#Original code by Wayne Porter


"""
from ..Script import Script


class TimeLapse(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return {
            "name": "Time Lapse",
            "key": "TimeLapse",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "trigger_command":
                {
                    "label": "Trigger camera command",
                    "description": "Gcode command used to trigger camera.",
                    "type": "str",
                    "default_value": "M240"
                },
                "pause_length":
                {
                    "label": "Pause length",
                    "description": "How long to wait (in ms) after camera was triggered.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms"
                },
                "park_print_head":
                {
                    "label": "Park Print Head",
                    "description": "Park the print head out of the way. Assumes absolute positioning.",
                    "type": "bool",
                    "default_value": true
                },
                "head_park_x":
                {
                    "label": "Park Print Head X",
                    "description": "What X location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "enabled": "park_print_head"
                },
                "head_park_y":
                {
                    "label": "Park Print Head Y",
                    "description": "What Y location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190,
                    "enabled": "park_print_head"
                },
                "park_feed_rate":
                {
                    "label": "Park Feed Rate",
                    "description": "How fast does the head move to the park coordinates.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 9000,
                    "enabled": "park_print_head"
                }
            }
        }

    def execute(self, data):
        feed_rate = self.getSettingValueByKey("park_feed_rate")
        park_print_head = self.getSettingValueByKey("park_print_head")
        x_park = self.getSettingValueByKey("head_park_x")
        y_park = self.getSettingValueByKey("head_park_y")
        trigger_command = self.getSettingValueByKey("trigger_command")
        pause_length = self.getSettingValueByKey("pause_length")
        gcode_to_append = ";TimeLapse Begin\n"
        last_x = 0
        last_y = 0

        if park_print_head:
            gcode_to_append += self.putValue(G=1, F=feed_rate,
                                             X=x_park, Y=y_park) + " ;Park print head\n"
        gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"
        gcode_to_append += trigger_command + " ;Snap Photo\n"
        gcode_to_append += self.putValue(G=4, P=pause_length) + " ;Wait for camera\n"

        for idx, layer in enumerate(data):
            for line in layer.split("\n"):
                if self.getValue(line, "G") in {0, 1}:  # Track X,Y location.
                    last_x = self.getValue(line, "X", last_x)
                    last_y = self.getValue(line, "Y", last_y)
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    layer += gcode_to_append

                    layer += "G0 X%s Y%s\n" % (last_x, last_y)

                    data[idx] = layer
                    break
        return data
"""
