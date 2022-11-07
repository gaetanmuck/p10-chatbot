
class UserModel:



    def __init__(self):
        self.destination = ''
        self.origin = ''
        self.go_date = ''
        self.back_date = ''
        self.budget = ''
        self.conv_id = -1



    def parse_entities(self, entities, first=False):
        """Parse the entities brought by the CLU, and put them in the object."""

        for ent in entities:
            # We have a confusion between the origin and destination.
            # Generally speaking, often in a natural discussion the destination is in the second position
            # It means that the origin is often first.
            # To increase the performance, when we have 2 destinations and 2 origins, 
            # We will take the 2nd destination and the 1st origin
            if first and ent['key'] == 'origin' and self.origin: pass
            else: 
                if ent['key'] == 'destination': self.destination = ent['value']
                if ent['key'] == 'origin': self.origin = ent['value']
                if ent['key'] == 'go_date': self.go_date = ent['value']
                if ent['key'] == 'back_date': self.back_date = ent['value']
                if ent['key'] == 'budget': self.budget = ent['value']



    def parse_entities_specific(self, entities, specific):
        """Parse the entities brought by the CLU, and put only the specific key in the object."""
        specific = specific.replace(' ', '_')

        for ent in entities:
            if ent['key'] == specific: 
                if ent['key'] == 'destination': self.destination = ent['value']
                if ent['key'] == 'origin': self.origin = ent['value']
                if ent['key'] == 'go_date': self.go_date = ent['value']
                if ent['key'] == 'back_date': self.back_date = ent['value']
                if ent['key'] == 'budget': self.budget = ent['value']
                return True

        return False


    def sum_up(self):
        """Create the sum up string to display to the user."""

        str = 'With information that you provided, I understood that you would like to go:\r\n'
        if self.destination: str += '  - To ' + self.destination + '\r\n'
        if self.origin: str += '  - From ' + self.origin + '\r\n'
        if self.go_date: str += '  - Leaving ' + self.go_date + '\r\n'
        if self.back_date: str += '  - Coming back ' + self.back_date + '\r\n'
        if self.budget: str += ' - With a maximum budget of ' + self.budget + '\r\n'
        str += 'Is that correct?'

        return str


    
    def get_missing(self):
        """Get missing required information that need to be asked to the user."""

        if self.destination == '': return 'destination'
        elif self.origin == '': return 'origin'
        elif self.go_date == '': return 'go_date'
        elif self.back_date == '': return 'back_date'
        elif self.budget == '': return 'budget'
        else: return 'complete'