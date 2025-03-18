import re
import yaml

class Filter:
  def __init__(self, synonym_file=None):
    self.synonyms = {}
    self.current_pos = 0
    self.filter_string = ''
    self.tree = None
    
    if synonym_file and self.__file_exists(synonym_file):
      with open(synonym_file, 'r') as file:
        self.synonyms = yaml.safe_load(file)
  
  def __file_exists(self, file_path):
    try:
      with open(file_path, 'r'):
        return True
    except FileNotFoundError:
      return False
  
  def parse(self, filter_string):
    self.filter_string = filter_string
    self.current_pos = 0
    return self.__parse_expression()
  
  def __parse_expression(self):
    terms = []
    operator = None
    
    while( self.current_pos < len(self.filter_string) ):
      self.__skip_whitespace()
      
      if( self.current_pos >= len(self.filter_string) ):
        break
      
      char = self.filter_string[self.current_pos]
      
      if( char == '(' ):
        self.current_pos += 1
        sub_expr = self.__parse_expression()
        if( self.current_pos < len(self.filter_string) and self.filter_string[self.current_pos] == ')' ):
          self.current_pos += 1
        terms.append(sub_expr)
      elif( self.filter_string[self.current_pos:self.current_pos+3].lower() == 'and' ):
        self.current_pos += 3
        operator = 'and'
      elif( self.filter_string[self.current_pos:self.current_pos+2].lower() == 'or' ):
        self.current_pos += 2
        operator = 'or'
      else:
        term = self.__parse_term()
        if( term is not None ):
          terms.append(term)
        else:
          break
    
    if( len(terms) == 1 ):
      return terms[0]
    
    return {
      'type': 'logical',
      'operator': operator or 'and',
      'terms': terms
    }
  
  def __parse_term(self):
    self.__skip_whitespace()
    
    # Check for field name (for record mode)
    field_name = self.__parse_identifier()
    self.__skip_whitespace()
    
    # Parse operators
    if( field_name ):
      operator = self.__parse_operator()
      if( not operator ):
        return None
      
      value = self.__parse_value()
      if( value is None ):
        return None
      
      return {
        'type': 'comparison',
        'field': field_name,
        'operator': operator,
        'value': value
      }
    
    # Full text mode
    value = self.__parse_value()
    if( value is None ):
      return None
    
    return {
      'type': 'text',
      'value': value
    }
  
  def __parse_identifier(self):
    identifier = ''
    while( self.current_pos < len(self.filter_string) ):
      char = self.filter_string[self.current_pos]
      if( re.match(r'[a-zA-Z0-9_.]', char) ):
        identifier += char
        self.current_pos += 1
      else:
        break
    
    return identifier or None
  
  def __parse_operator(self):
    operators = ['=', '!=', '>', '<', '>=', '<=', 'in', '!in', 'contains_any', 'contains_all']
    for op in operators:
      if( self.filter_string[self.current_pos:self.current_pos+len(op)] == op ):
        self.current_pos += len(op)
        return op
    return None
  
  def __parse_value(self):
    self.__skip_whitespace()
    
    if( self.current_pos >= len(self.filter_string) ):
      return None
    
    char = self.filter_string[self.current_pos]
    
    # String
    if( char in ('"', "'") ):
      self.current_pos += 1
      value = ''
      while( self.current_pos < len(self.filter_string) ):
        if( self.filter_string[self.current_pos] == char ):
          self.current_pos += 1
          return value
        value += self.filter_string[self.current_pos]
        self.current_pos += 1
    
    # Regex
    if( char == '/' ):
      self.current_pos += 1
      pattern = ''
      while( self.current_pos < len(self.filter_string) ):
        if( self.filter_string[self.current_pos] == '/' ):
          self.current_pos += 1
          # Get regex flags
          flags = ''
          while( self.current_pos < len(self.filter_string) and 
                re.match(r'[a-z]', self.filter_string[self.current_pos]) ):
            flags += self.filter_string[self.current_pos]
            self.current_pos += 1
          return {'type': 'regex', 'pattern': pattern, 'flags': flags}
        pattern += self.filter_string[self.current_pos]
        self.current_pos += 1
    
    # Array
    if( char == '[' ):
      self.current_pos += 1
      values = []
      while( self.current_pos < len(self.filter_string) ):
        self.__skip_whitespace()
        if( self.filter_string[self.current_pos] == ']' ):
          self.current_pos += 1
          return values
        if( self.filter_string[self.current_pos] == ',' ):
          self.current_pos += 1
          continue
        value = self.__parse_value()
        if( value is not None ):
          values.append(value)
    
    # Numbers
    if( re.match(r'[0-9.-]', char) ):
      number = ''
      while( self.current_pos < len(self.filter_string) and 
            re.match(r'[0-9.-]', self.filter_string[self.current_pos]) ):
        number += self.filter_string[self.current_pos]
        self.current_pos += 1
      if( number.isdigit() or (number.count('.') == 1 and number.replace('.', '').isdigit()) ):
        return float(number)
    
    # Boolean and null
    constants = {'true': True, 'false': False, 'null': None}
    for word, value in constants.items():
      if( self.filter_string[self.current_pos:self.current_pos+len(word)] == word ):
        self.current_pos += len(word)
        return value
    
    return None
  
  def __skip_whitespace(self):
    while( self.current_pos < len(self.filter_string) and 
          re.match(r'\s', self.filter_string[self.current_pos]) ):
      self.current_pos += 1
  
  def check(self, input_data, tree=None):
    if( tree is None ):
      tree = self.tree
    
    if( not isinstance(tree, dict) ):
      return False
    
    if( tree['type'] == 'logical' ):
      results = [self.check(input_data, term) for term in tree['terms']]
      
      return all(results) if tree['operator'] == 'and' else any(results)
    
    if( tree['type'] == 'text' ):
      if( isinstance(input_data, str) ):
        if( isinstance(tree['value'], dict) and tree['value']['type'] == 'regex' ):
          flags = 0
          if( 'i' in tree['value']['flags'] ):
            flags |= re.IGNORECASE
          return bool(re.search(tree['value']['pattern'], input_data, flags))
        
        search_values = [tree['value']]
        if( tree['value'] in self.synonyms ):
          search_values.extend(self.synonyms[tree['value']])
        
        for value in search_values:
          if( value.lower() in input_data.lower() ):
            return True
      return False
    
    if( tree['type'] == 'comparison' ):
      value = self.__get_nested_value(input_data, tree['field'])
      
      if( tree['operator'] == '=' ):
        if( isinstance(tree['value'], dict) and tree['value']['type'] == 'regex' ):
          flags = 0
          if( 'i' in tree['value']['flags'] ):
            flags |= re.IGNORECASE
          return bool(re.search(tree['value']['pattern'], str(value), flags))
        return value == tree['value']
      
      elif( tree['operator'] == '!=' ):
        if( isinstance(tree['value'], dict) and tree['value']['type'] == 'regex' ):
          flags = 0
          if( 'i' in tree['value']['flags'] ):
            flags |= re.IGNORECASE
          return not bool(re.search(tree['value']['pattern'], str(value), flags))
        return value != tree['value']
      
      elif( tree['operator'] == '>' ):
        return value > tree['value']
      
      elif( tree['operator'] == '<' ):
        return value < tree['value']
      
      elif( tree['operator'] == '>=' ):
        return value >= tree['value']
      
      elif( tree['operator'] == '<=' ):
        return value <= tree['value']
      
      elif( tree['operator'] == 'in' ):
        return value in tree['value']
      
      elif( tree['operator'] == '!in' ):
        return value not in tree['value']
      
      elif( tree['operator'] == 'contains_any' ):
        return bool(set(value) & set(tree['value']))
      
      elif( tree['operator'] == 'contains_all' ):
        return set(tree['value']).issubset(set(value))
    
    return False
  
  def __get_nested_value(self, input_data, field):
    parts = field.split('.')
    current = input_data
    
    for part in parts:
      if( not isinstance(current, dict) or part not in current ):
        return None
      current = current[part]
    
    return current