from mesa.discrete_space import CellAgent

class MoneyAgent(CellAgent):

    def __init__(self, model, cell, mode):
        super().__init__(model)
        self.cell = cell
        self.wealth = 1
        self.mode = mode

    def move(self):
        self.cell = self.cell.neighborhood.select_random_cell()

    def give_money(self):
        cellmates = [a for a in self.cell.agents if a is not self]

        if cellmates: 
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def give_money_to_poor(self):
            cellmates = [a for a in self.cell.agents if a is not self]

            if cellmates: 
                poorer_cellmates = [a for a in cellmates if a.wealth <= self.wealth] 
                
                if poorer_cellmates and self.wealth > 0: 
                    other = self.random.choice(poorer_cellmates)
                    other.wealth += 1
                    self.wealth -= 1

    def step(self):
        if(self.mode == 3):
            if self.random.random() < 0.5: self.move()
        else:   
            self.move()

        if self.wealth > 0:
            if(self.mode == 1 or self.mode == 3): self.give_money()
            elif(self.mode == 2): self.give_money_to_poor()

