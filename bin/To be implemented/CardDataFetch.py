import requests
from typing import Any
from FastDebugger import fd
from traceback import format_exc
import serial
# from crop_and_read import collector_number, set_name
from car import car

class InvalidDataError(Exception):
    pass

class Card:
    def __init__(self, card_set:str, card_number:int|str) -> None:
        def _api_fetch_json_data(card_set:str, card_number:int|str) -> dict:
            """Fetches the card data from the Scryfall API and returns it as a dictionary.
            
            Parameters
            ----------
            card_set: str
                The set of the card.
            card_number: int | str
                The number of the card in the set.
            
            Returns
            -------
            dict
                The card data as a dictionary.
            """
            api_url = f"https://api.scryfall.com/cards/{card_set.lower()}/{str(int(card_number))}"
            response = requests.get(api_url)
            if response.status_code != 200:
                raise Exception(f'Error fetching card data from url {api_url!r}: {response.status_code}\n{response.text}')
            
            return response.json()

        def _copy_attributes_from_data() -> None:
            """Copies the attributes from the fetched data to the card object."""
            for key, value in self._json_data.items():
                setattr(self, key, value)

        # def _api_fetch_poro_data() -> dict:
            
        #     card_id = self.get_value('id')
        #     api_url_poro = f'https://poromagia.com/store_manager/card_api/?access_token=4f02d606&id={card_id}'
        #     response = requests.get(api_url_poro,
        #                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'},
        #                 json=True)
        #     if response.status_code != 200:
        #         raise Exception(f'Error fetching card data from url {api_url_poro!r}: {response.status_code}\n{response.text}')
        
        def _get_poro_price(key:str) -> float:
            """Fetches the card price from the Poro API and returns it.
            
            Parameters
            ----------
            key: str
            The value to fetch from the Poro API.
            
            Returns
            -------
            float
            The price of the card.
            """
            card_id = self.get_value('id')
            api_url_poro = f'https://poromagia.com/store_manager/card_api/?access_token=4f02d606&id={card_id}'
            response = requests.get(api_url_poro,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'},
                        json=True)
            if response.status_code != 200:
                raise Exception(f'Error fetching card data from url {api_url_poro!r}: {response.status_code}\n{response.text}')
            
            try:
                    poro_price = response.json().get(key, 0.0)
                    if poro_price in ['NoneType', None]:
                        raise ValueError
                    return float(poro_price)
            except ValueError:
                    return 0.0

        def _get_from_price(key:str) -> float:
            """Returns the price of the card from the given dictionary.
            
            Parameters
            ----------
            key: str
                Get the price of the card from the dictionary.
                
            Returns
            -------
            float
                The price of the card.
            """
            try:
                price = self.get_value('prices', {}).get(key, 0.0)
                if price in ['NoneType', None]:
                    raise ValueError
                return float(price)
            except ValueError:
                return 0.0

        self._json_data = _api_fetch_json_data(card_set, card_number)
        _copy_attributes_from_data()

        # Prices
        self.eur_price = _get_from_price('eur')
        self.eur_foil_price = _get_from_price('eur_foil')
        self.poro_price = _get_poro_price('price')
sort_cards
        # Fix color_identity if it's empty
        if self.get_value('color_identity') == []:
            self.color_identity = ['C']

    def get_value(self, key:str, def_ret_val:Any=None) -> Any:
        """Returns the value of the given attribute."""
        try:
            return getattr(self, key)
        except AttributeError:
            return def_ret_val

    def debug_output(self, dont_print:list[str]=[], only_print:list[str]=[]) -> None:
        """Prints the card data to the console.
        
        Parameters
        ----------
        dont_print: list[str]
            List of attributes not to print.
        only_print: list[str]
            List of attributes to print.
        """
        for key, value in self.__dict__.items():
            if only_print and key not in only_print:
                continue

            elif key[0] == '_' or key in dont_print or 'uri' in key  or 'object' in key or 'rank' in key:   # or 'id' in key[-3:]
                continue

            print(f'-- {key!r}: {value}')
        print()


    def get_data_from_json(self, try_get_val:str, err_return_val:Any='N/A') -> Any:
        """This function tries to fetch the card data from the given dictionary, and returns the err_return_val if the given data is not found.

        data: Dictionary from which to fetch the card data, dictionaries in use are [data, prices]
        try_get_val: Name of the card data to fetch from the dictionary data
        err_return_val: Value to return if the card data is not found
        """
        def _catch_error() -> None:
            print(f'Error fetching {try_get_val!r}')
            return err_return_val

        try:
            val = self._json_data[try_get_val]

            if val == 'NoneType' or val is None:
                raise TypeError

            else:
                return val
            
        except  KeyError:                            
            if 'card_faces' not in self._json_data:
                return _catch_error()
            
            return self._json_data['card_faces'][0].get(try_get_val, err_return_val)

        except (TypeError):
            return _catch_error()
    
    def search_old_card(scanned_name:str, artist_name:str) -> None:
        
        pass

    #TODO: search by card name to match & sort older cards
    # https://scryfall.com/docs/syntax  # Syntax for searching cards
    # https://scryfall.com/docs/api/cards/search
    # https://api.scryfall.com/cards/search?order=released&q=name:sol_ring+unique:prints #[unique:arts] to get onlu single copy of each art
    # https://api.scryfall.com/cards/search?order=released&q=name:sol_ring+unique:prints+year%3C2016 #search for cards printed before 2016

def main():
    sort_criteria = None    # Criteria by which the card is sorted
    sort_to_box = None             # Box to which the card is sorted
    path_to_card_list = None    # Specify the path to the card_list JSON file
    
    global card_list
    card_list = None        # List of cards

    card_str_lst = ['j22 55', 'lci 88', 'c21 149', 'scd 245', 'scd 262', 'scd 269', 'mom 0232', 'scd 172', 'scd 099', 'woe 272', 'clb 896', 'ogw 67', 'ogw 001'] # List of card strings
    
    # collector_number = int(collector_number.split('/')[0].strip())
    # c = Card(set_name, collector_number)      # Card Being Tested
    # c = Card("DMR", "098")
    # card_obj_lst = [Card(*c.split(' ')) for c in card_str_lst]  # List of card objects


# Define a function to sort the cards by the criteria
def sort_cards(sort_criteria:str, c_value:float=None) -> Any:
    """ Sorts the cards by the given criteria and returns the box to which the card is sorted.
    
    Parameters
    ----------
    sort_criteria: str
        The sorting criteria to use [price, color, type, card_list]
    c_value: float
        The value above which the card is considered expensive.
    
    Returns
    -------
    int
        The box to which the card is sorted as int.
    """
    def ser_print(msg):
        if ser:
            ser.write(msg)

    card_data = car()
    # collector_number, rarity, set_code, language = int(card_data[0].split('/')[0].strip()), card_data[1], card_data[2], card_data[3]
    
    collector_number = int(card_data["collector_number"].split('/')[0].strip())
    set_code = card_data["set_name"]
    
    c = Card(set_code, collector_number)  #c and c_value need to be defiend in order for the funciton to work
    # c = Card('OGW', '001')        # Card fro debugging

    type_line = c.get_value('type_line')
    color_identity = c.get_value('color_identity')
    name = c.get_value('name')

    ser = False     # For debugging without printing to serial
    # ser = serial.Serial('/dev/ttyUSB0', 9600)  # Open serial port
    # fd(set_code, collector_number, card_data)

    match sort_criteria:
        case 'price': 
            if 'Land' in type_line and c.poro_price < c_value:
                print('This card is a Land, so it goes to Box1')
                ser_print(b'1\n')
                sort_to_box = 1

            elif -1 < c.poro_price < c_value:
                print(f'This card is Cheap (below {c_value}), so it goes to Box2')
                ser_print(b'2\n')
                sort_to_box = 2

            elif c.poro_price > c_value:
                print(f'This card is Expensive (above {c_value}), so it goes to Box3')
                ser_print(b'3\n')
                sort_to_box = 3

            else:
                print('This card was not recognized, so it goes to Box4')
                ser_print(b'4\n')
                sort_to_box = 1
                raise InvalidDataError(f'Invalid price {c.poro_price!r}')
       
        case 'color':
            _color_temp = ''.join(color_identity)

            if 'Land' in type_line and c.poro_price < c_value:
                print('This card is a Land, so it goes to Box1')
                ser_print(b'1\n')
                sort_to_box = 1

            elif len(_color_temp) > 1:
                print('This card is Multicolor, so it goes to Box4')
                ser_print(b'4\n')
                sort_to_box = 4
            
            elif _color_temp in ('W', 'U', 'B'):
                print('This card is White / Blue or Black, so it goes to Box2')
                ser_print(b'2\n')
                sort_to_box = 2

            elif _color_temp in ('R', 'G', 'C'):
                print('This card is Red / Green or Colorless, so it goes to Box3')
                ser_print(b'3\n')
                sort_to_box = 3
            
            else:
                raise InvalidDataError(f'Invalid color_identity {_color_temp!r}')
        
        case 'type':
            if 'Creature' in type_line or 'Planeswalker' in type_line:
                print('This card is a Creature or Planeswalker, so it goes to Box2')
                ser_print(b'2\n')
                sort_to_box = 2

            elif type_line == 'Instant' or type_line == 'Sorcery':
                print('This card is an Instant or Sorcery, so it goes to Box3')
                ser_print(b'3\n')
                sort_to_box = 3
            
            elif 'Enchantment' in type_line or 'Artifact' in type_line:
                print('This card is an Enchantment or Artifact, so it goes to Box4')
                ser_print(b'4\n')
                sort_to_box = 4
            
            else:
                print('This card is a Land, so it goes to Box1')
                ser_print(b'1\n')
                sort_to_box = 1
                raise InvalidDataError(f'Invalid Type {type_line!r}')
        
        case 'card_list':
            if 'Land' in type_line and not name in card_list:
                print('This card is a Land, not in the list, so it goes to Box1')
                ser_print(b'1\n')
                sort_to_box = 1

            elif name in card_list:
                print('This card is in the list, so it goes to Box2')
                ser_print(b'2\n')
                sort_to_box = 2

            else:
                print('This card is not in the list, so it goes to Box3')
                ser_print(b'3\n')
                sort_to_box = 3

        case _:
            raise InvalidDataError(f'Invalid sort_criteria {sort_criteria!r}')
             
    print('sort_to_box:', sort_to_box)
    print('sort_criteria:', sort_criteria)
    print('name:', name)
    print('color identity:', color_identity)

# c = Card(set_name, collector_number)
# c.debug_output(only_print=['id', 'name', 'lang', 'mana_cost', 'cmc', 'type_line', 'power', 'toughness', 'colors', 'color_identity', 'loyalty', 'prices', 'eur_price', 'eur_foil_price'])
sort_cards('price', 1)
# sort_cards('color')
# fd(c.poro_price)
# main()

# test = car()
# fd(test)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')