#//////////////////////////////////////////////////////////////////////////////
# FILE: build-emx.py
# AUTHOR: David Ruvolo
# CREATED: 2022-06-16
# MODIFIED: 2022-11-30
# PURPOSE: Render EMX files for Stats package
# STATUS: stable
# PACKAGES: yamlemxconvert
# COMMENTS: NA
#//////////////////////////////////////////////////////////////////////////////

from clize import run
import yamlemxconvert
import yaml

def buildModel(pathToProfile):
  """Build Emx Model
  :profile pathToProfile: location of the yaml-profile file
  """
  with open(pathToProfile, 'r') as file:
    profile=yaml.safe_load(file)
    file.close()
    del file
      
  if 'buildOptions' not in profile:
    raise KeyError('No build options defined')
      
  # build emx1 version with options
  emx1options=profile['buildOptions']['emx1']
  if emx1options['active']:
    emx1 = yamlemxconvert.Convert(files=profile['modelFilePath'])
    emx1.convert()
    emx1.compileSemanticTags()
    
    # override package-level labels
    if profile.get('setEmxLabels'):
      newPackageLabels=profile['setEmxLabels']
      if newPackageLabels.get('setPackageLabel'):
        emx1.packages[0]['label']=newPackageLabels['setPackageLabel']
    
    # override labels
    if emx1options.get('overrideLabels'):
      # override entity labels
      for table in profile['overrideEmxAttributes']:
        tableOverrides=profile['overrideEmxAttributes'][table]
        
        # rename entity label
        if tableOverrides.get('overrideTableLabelWith'):
          for row in emx1.entities:
            if row['name']== table:
              row['label']=tableOverrides['overrideTableLabelWith']
                  
        # rename attribute labels
        if tableOverrides.get('attributeLabelsToOverride'):
          newLabels=tableOverrides.get('attributeLabelsToOverride')
          for row in emx1.attributes:
            for label in newLabels.keys():
              tableName="ernstats_" + table
              if (row['entity']==tableName) and (row['name']==label):
                row['label']=newLabels[label]    

    # override visibility: hide attributes if defined
    if emx1options.get('overrideVisibility'): 
      globalHiddenAttribs=profile['overrideEmxAttributes'].get('_all',{}).get('attributesToHide')
      for row in emx1.attributes:
        # hide if in global definitions
        if row['name'] in globalHiddenAttribs:
          row['visible']=False
              
        # hide in table definitions
        tableName=row['entity'].split('_')[1]
        if tableName in profile['overrideEmxAttributes']:
          tableOverrides=profile['overrideEmxAttributes'][tableName]
          if 'attributesToHide' in tableOverrides:
            tableAttribsToHide=tableOverrides['attributesToHide']
            if row['name'] in tableAttribsToHide:
              row['visible']=False

    emx1.write(name=profile['name'], outDir=emx1options['outputDir'])    
    schemaPath = emx1options['schemasDir'] + "/" + profile['name'] + "_schema.md"
    emx1.write_schema(path=schemaPath)
      
  # build emx2 version with options
  emx2options=profile['buildOptions']['emx2']
  if emx2options['active']:
    emx2=yamlemxconvert.Convert2(file=profile['modelFilePath'])
    emx2.convert()
    emx2.write(name=profile['name'], outDir=emx2options['outputDir'])
  
if __name__ == '__main__':
  run(buildModel)
