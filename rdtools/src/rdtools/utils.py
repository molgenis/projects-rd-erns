from datetime import datetime
from pytz import timezone

def print2(*args):
  """Print2
  Extension of print but all messages are printed with a timestamp. By default,
  the timezone is 'Europe/Amsterdam'.
  
  @examples
  ```
  print2('Hello World')
  
  data = [{'id': value} for value in range(0,100)]
  print2('The total number of records is', len(data))
  ```
  """
  message = ' '.join(map(str, args))
  time = datetime.now(tz=timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
  print(f'[{time}] {message}')