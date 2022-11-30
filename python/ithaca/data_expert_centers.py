#///////////////////////////////////////////////////////////////////////////////
# FILE: data_source_expert_centers.py
# AUTHOR: David Ruvolo
# CREATED: 2022-11-30
# MODIFIED: 2022-11-30
# PURPOSE: get a list of expert centers from the project website
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: You will need to install selenium (via pip). In addition, selenium
# requires the Java SDE development kit. Please see the docs for installiation
# instructions: https://selenium-python.readthedocs.io/installation.html
#///////////////////////////////////////////////////////////////////////////////

from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
from datatable import dt, f
import csv

# start session
driver = webdriver.Firefox()
driver.get("https://ern-ithaca.eu/about-us/expert-centers/")


# find map navigation buttons and click the 'Expert Centers List' button
# this is bit nasty, but manually enter each div too find the second button.
btn = driver.find_element(
  by=By.CSS_SELECTOR,
  value="#interactive-map-navigation div div.rounded-pill div:nth-child(2) button.btn-primary"
)

btn.click()

# Find the list of expert centers and select all list elements
expertCenters = driver.find_elements(
  by = By.CSS_SELECTOR,
  value = '#interactive-map-wrapper-list li.list-item-tertiary'
)

rawdata = []
for element in tqdm(expertCenters):
  rawdata.append({
    'displayName': element.find_element(By.CSS_SELECTOR, 'h2.list-item-title').text,
    'country': element.find_element(By.CSS_SELECTOR,'span.badge').text,
    'representative': element.find_element(By.CSS_SELECTOR, 'div.list-item-text.text-primary p').text,
    'status': element.find_element(By.CSS_SELECTOR, 'div.list-item-footer div span:nth-child(2)').text,
    'href': element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
  })
  

# do some light cleaning -- geocoding with ror isn't really possible as the
# organisation names seem a bit vague. It's best to clean the data here and
# manually lookup information.
data = dt.Frame(rawdata)

data['country'] = dt.Frame([
  country.title()
  for country in data['country'].to_list()[0]
])

data['representative'] = dt.Frame([
  rep.replace('Representative:','').strip()
  for rep in data['representative'].to_list()[0]
])

data[[
  'latitude',
  'longitude',
  'hasSubmittedData',
  'city',
  'code',
  'codesystem',
  'iri',
  'projectName'
]] = None


# save data
data.to_pandas() \
  .to_csv(
    'data/ern_ithaca_expert_centers.csv',
    index=False,
    quoting=csv.QUOTE_ALL
  )

driver.close()
