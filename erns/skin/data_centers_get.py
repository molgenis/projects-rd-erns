#///////////////////////////////////////////////////////////////////////////////
# FILE: data_centers_get.py
# AUTHOR: David Ruvolo
# CREATED: 2023-02-22
# MODIFIED: 2023-02-27
# PURPOSE: Compile a list of reference centers
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datatable import dt, f
from os import path
import csv
import re

# start session
driver = webdriver.Firefox()
driver.get('https://ern-skin.eu/reference-centers/')

# find all reference centre containers (grouped by country)
containers = driver.find_elements(
  by= By.CSS_SELECTOR,
  value = 'div.post-content div.fusion-fullwidth.fullwidth-box.fusion-equal-height-columns'
)

# for each container (i.e., country), find all the centers and extract <a> info
data = []
for container in containers:
  try:
    src = container.find_element(By.CSS_SELECTOR,'div.fusion-image-element img').get_attribute('src')
    centers = container.find_elements(By.CSS_SELECTOR,'.fusion-text p')
    for center in centers:
      link = center.find_element(By.CSS_SELECTOR, 'a')
      data.append({
        'image': src,
        'title': link.get_attribute('title'),
        'href': link.get_attribute('href'),
        'name': link.text,
      })
  except NoSuchElementException as error:
    if error.msg == 'Unable to locate element: a':
      data.append({
        'image': src,
        'title': center.text,
        'href': None,
        'name': center.text
      })
    else:
      print(error.msg)

#///////////////////////////////////////

# convert to datatable object
centersDT = dt.Frame(data)


# trim all trailing whitespace
for column in centersDT.names:
  centersDT[column] = dt.Frame([
    value.strip().replace('\n','') if value else value
    for value in centersDT[:, column].to_list()[0]
  ])
  
centersDT.names
centersDT['image']
centersDT['title']
centersDT['href']
centersDT['name']

# # Drop non-relevant rows (i.e., non-centers)
centersDT=centersDT[dt.re.match(f.name,'Thanks to.*')==False,:]

# # Extract Country from image url
centersDT['country'] = dt.Frame([
  re.sub(
    pattern=r'(iconfinder_[0-9]{1,}_ensign_flag_nation_|.png|[-_](e)?[0-9]{1,})',
    repl='',
    string=path.basename(value).lower()
  )
  for value in centersDT['image'].to_list()[0]
])


# # drop columns and rename
del centersDT['image']
del centersDT['title']

centersDT.names = {
  'href': 'centerProjectUrl',
  'name': 'projectName'
}

# save to file and manually look for ROR entries
centersDT.to_pandas() \
  .to_csv(
    'data/ern_skin_reference_centers.csv',
    quoting=csv.QUOTE_ALL,
    sep=',',
    index=False,
    encoding='utf-16'
  )

driver.close()