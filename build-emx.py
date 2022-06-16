
import yamlemxconvert

emx1 = yamlemxconvert.Convert(files=['model/ernstats.yaml'])
emx2 = yamlemxconvert.Convert2(file='model/ernstats.yaml')

emx1.convert()
emx2.convert()

emx1.write(name="ernstats", outDir="model")
emx2.write(name="ernstats_emx2", outDir="model")
