#Import Statements
from drafter import *
from dataclasses import dataclass
from molmass import Formula
from bakery import assert_equal



#Github Info
set_website_title("Stoichiometry Calculator")
set_site_information(
    author="Matthew Li",
    description="",
    sources=["https://pypi.org/project/molmass/", "https://drafter-edu.github.io/drafter/"],
    planning=["CS1 Final Project 1_ Design.docx", "CS1 Final Project 0_ Pick a Problem.docx"],
    links=["https://github.com/mattli-26/Stoichiometry-Calculator"]
)
hide_debug_information()
set_website_framed(False)



#Defining Dataclasses
@dataclass
class Compound:
    """
    Represents the different value of a chemical compound.
    
    Attributes:
        formula(str): the chemical formula of the compound
        molar(float): the molecular weight of the compound
        coefficient(int): the coefficient of the compound in the reaction formula
        initial(float): the starting amount of the compound in the reaction, in grams
        final(float): the ending amount of the compound in the reaction, in grams
    """
    
    formula: str
    molar: float
    coefficient: int
    initial: float
    final: float

empty_compound = Compound("", 0, 0, 0., 0.)

@dataclass
class State:
    """
    Represents the state of the program.
    
    Attributes:
        formula(str): the formula of the chemical reaction input by user
        reactants(list[Compound]): the reactants of the reaction
        products(list[Compound]): the products of the reaction
        error(str): allows an error message to be displayed
    """
    
    formula: str
    reactants: list[Compound]
    products: list[Compound]
    error: str
    


#Helper Functions
def update_state(reaction: str) -> State:
    """
    Given a reaction formula in the correct format, it updates the State dataclass.
    If the reaction is not in the correct format, a special State will be returned.
    
    Arguments:
        reaction(str): the chemical reaction formula
    Return:
        State: the updated state of the program
    """
    #Reaction Formula
    if not reaction:
        return State("", [], [], "INVALID FORMAT")
    elif "->" not in reaction:
        return State("", [], [], "INVALID FORMAT")
    elif len(reaction.split("->")) != 2:
        return State("", [], [], "INVALID FORMAT")
    else:
        state_formula = reaction
    
    #Reactants
    reactants = reaction.split("->")[0]
    reactant_list = reactants.split("+")
    for i, reactant in enumerate(reactant_list):
        reactant_list[i] = reactant.strip()
        if reactant.strip().isdigit():
            return State("", [], [], "INVALID FORMAT")
    state_reactants = input_compounds(reactant_list)
    
    #Products
    products = reaction.split("->")[1]
    product_list = products.split("+")
    for i, product in enumerate(product_list):
        product_list[i] = product.strip()
        if product.strip().isdigit():
            return State("", [], [], "INVALID FORMAT")
    state_products = input_compounds(product_list)
    
    return State(state_formula, state_reactants, state_products, "")


def input_compounds(compounds: list[str]) -> list[Compound]:
    """
    Given a list of compounds, this function converts them into a list of Comounds so they can be input
    into the state dataclass.
    
    Arguments:
        compounds(list[str]): the list of compound represented by string, can be either reactants or products
    Return:
        list[Compound]: the list of compound represented by Compound dataclass, can be input into state
    """
    
    updated_compounds = []
    for compound in compounds:
        i = 0
        while compound[i].isdigit():
            i += 1
        formula = compound[i:]
        molar = Formula(formula).mass
        if i:
            coefficient = int(compound[:i])
        else:
            coefficient = 1
        updated_compounds.append(Compound(formula, molar, coefficient, 0., 0.))
    while len(updated_compounds) < 3:
        updated_compounds.append(Compound("", 0, 0, 0., 0.))
    return updated_compounds

assert_equal(input_compounds(["6CO2", "6H2O"]), [Compound("CO2", 44.00955, 6, 0., 0.),
                                                 Compound("H2O", 18.015287, 6, 0., 0.), empty_compound])
assert_equal(input_compounds(["C6H12O6"]), [Compound("C6H12O6", 180.156162, 1, 0., 0.),
                                            empty_compound, empty_compound])


def calculate_initial_reactant(state: State, known: Compound) -> State:
    """
    Calculates the amount of reactants needed in grams, given the starting amount of one other reactant.
    
    Arguments:
        state(State): the current state of the program, including information of reactants and prodcuts
        known(Compound): the starting value of the stoichiometry calculation
    Return:
        State: the updated state of the program, with the calculated values updated
    """
    
    known_mol = known.initial / known.molar
    for i, reactant in enumerate(state.reactants):
        if reactant.formula != known.formula and reactant.formula:
            reactant_mol = known_mol / known.coefficient * reactant.coefficient
            state.reactants[i].initial = reactant_mol * reactant.molar
        elif not reactant.formula:
            state.reactants[i].initial = 0.
    return state


def calculate_final_reactant(state: State, known: Compound) -> State:
    """
    Calculates the amount of reactants remaining in grams, given the starting amount of one reactant.
    
    Arguments:
        state(State): the current state of the program
        known(Compound): the starting value of the stoichiometry calculation
    Return:
        State: the updated state of the program, with the final values of products updated
    """
    
    known_mol = known.initial / known.molar
    for i, reactant in enumerate(state.reactants):
        if reactant.formula and reactant.initial:
            reactant_mol = known_mol / known.coefficient * reactant.coefficient
            state.reactants[i].final = reactant.initial - reactant_mol * reactant.molar
        else:
            reactant.final = 0.
    return state


def calculate_final_product(state: State, known: Compound) -> State:
    """
    Calculates the amount of products produced in grams, given the starting amount of one reactant.
    
    Arguments:
        state(State): the current state of the program
        known(Compound): the starting value of the stoichiometry calculation
    Return:
        State: the updated state of the program, with the calculated values updated
    """
    
    known_mol = known.initial / known.molar
    for i, product in enumerate(state.products):
        if product.formula:
            product_mol = known_mol / known.coefficient * product.coefficient
            state.products[i].final = product_mol * product.molar
        else:
            state.products[i].final = 0.
    return state


def identify_limiting(reactants: list[Compound]) -> int:
    """
    Givene a list of reactants, this function identifies the index of the limiting reactant.
    
    Arguments:
        reactants(list[Compound]): the list of reactants with amounts input by user
    Return:
        int: the index of the limiting reactant in the list
    """
    
    reaction_list = []
    for reactant in reactants:
        if reactant.formula and reactant.initial:
            reaction = reactant.initial / reactant.molar / reactant.coefficient
            reaction_list.append(reaction)
        else:
            reaction_list.append(-1.)
    minimum = 10**50
    minimum_i = -1
    for i, reaction in enumerate(reaction_list):
        if reaction < minimum and reaction > 0:
            minimum = reaction
            minimum_i = i
    return minimum_i
        




#Route Functions
@route
def index(state: State) -> Page:
    """
    The main page of the program, where user can input formula and information of reactant.
    
    Arguments:
        state(State): the current state of the program
    Return:
        Page: the main program page
    """
    
    return Page(
        state,
        [
            Header("Stoichiometry Calculator"),
            "Your reaction solver",
            "\n",
            "Reaction Formula: ",
            "\n",
            "Please input in format \"Reactant1 + Reactant2 -> Product1 + Product2\"",
            "\n",
            state.error,
            "\n",
            TextBox("reaction_formula", state.formula, style_width="800px"),
            "\n",
            Button("Input Formula", "input_formula")
        ],
    )


@route
def input_formula(state: State, reaction_formula: str) -> Page:
    """
    Given the reaction formula, this button updates the State and outputs another page.
    
    Arguments:
        state(State): the current state of the program
        reaction_formula(str): formula of the chemical reaction input by user in textbox      
    Return:
        Page: a page for the user to confirm the reactants and products of the reaction
    """
    
    state = update_state(reaction_formula)
    if state.error == "INVALID FORMAT":
        return index(state)
    content = [Header(state.formula)]
    for i, reactant in enumerate(state.reactants):
        if reactant.formula:
            content.append("Reactant " + str(i + 1) + ": " + reactant.formula + "\n")
    for i, product in enumerate(state.products):
        if product.formula:
            content.append("Product " + str(i + 1) + ": " + product.formula + "\n")
    content.append(Button("Edit", "edit_formula"))
    content.append(Button("Confirm", "confirm_formula"))
    return Page(
        state,
        content,
    )


@route
def edit_formula(state: State) -> Page:
    """
    Returns the user to the home page without changing the state of the program.
    
    Arguments:
        state(State): the current state of the program
    Return:
        Page: the main page of the program
    """
    return index(state)


@route
def confirm_formula(state: State) -> Page:
    """
    Continues the program to the next page, where the initial amounts will be input.
    
    Arguments:
        state(State): the current state of the program
    Return:
        Page: a page that prompts user to input amount of different compounds
    """
    
    content = [Header("Input amounts in grams" + state.error), "Input either Reactants or Products\n",
               "DO NOT input both sides\n", "Input minimum of 1 textbox\n", "Leave unknowns blank\n", "\n", "\n"]
    content.append("The reaction starts with")
    for i, reactant in enumerate(state.reactants):
        if reactant.formula:
            content.append("\n" + reactant.formula + ": ")
            content.append(TextBox("reactant" + str(i + 1) + "_initial", ""))
        else:
            content.append("\n")
            content.append(TextBox("reactant" + str(i + 1) + "_initial", "", style_display="none"))
    
    content.append("\n")
    content.append("The reaction ends with")
    for i, product in enumerate(state.products):
        if product.formula:
            content.append("\n" + product.formula + ": ")
            content.append(TextBox("product" + str(i + 1) + "_final", ""))
        else:
            content.append("\n")
            content.append(TextBox("product" + str(i + 1) + "_final", "", style_display="none"))
    content.append("\n" + "\n")
    content.append(Button("Input Values", "input_amounts"))
    return Page(
        state,
        content,
        )


@route
def input_amounts(state: State, reactant1_initial: str, reactant2_initial: str, reactant3_initial: str,
                   product1_final: str, product2_final: str, product3_final: str) -> Page:
    """
    This function updates the input amounts into state, determines which type of calculation to run,
    calls the appropriate function to run the calculation, and displays the results as a Page.
    
    Arguments:
        state(State): the current state of the program
        reactant1_initial(str): amount of reactant 1 input by user in grams
        reactant2_initial(str): amount of reactant 2 input by user in grams
        reactant3_initial(str): amount of reactant 3 input by user in grams
        product1_final(str): amount of product 1 input by user in grams
        product2_final(str): amount of product 2 input by user in grams
        product3_final(str): amount of product 3 input by user in grams
    Return:
        Page: displays the results of the calculation
    """
    
    content = []
    
    #Update State
    reactants_initials = [reactant1_initial, reactant2_initial, reactant3_initial]
    for i, reactant_initial in enumerate(reactants_initials):
        if reactant_initial:
            state.reactants[i].initial = float(reactant_initial)
            
        else:
            state.reactants[i].initial = 0.
        reactants_initials[i] = bool(reactant_initial)
    products_finals = [product1_final, product2_final, product3_final]
    for i, product_final in enumerate(products_finals):
        if product_final:
            state.products[i].final = float(product_final)
        else:
            state.products[i].final = 0.
        products_finals[i] = bool(product_final)
            
    #Calculating Number of Inputs
    sum_reactants = 0
    given_reactants = []
    for i, reactant in enumerate(reactants_initials):
        sum_reactants += reactant
        if reactant:
            given_reactants.append(i)
    sum_products = 0
    given_products = []
    for i, product in enumerate(products_finals):
        sum_products += product
        if product:
            given_products.append(i)
        
    #Reject Input
    if sum_reactants and sum_products:
        state.error = "     DO NOT ENTER BOTH SIDES"
        return confirm_formula(state)
    
    #Given Reactant
    content = [Header("Result")]
    #Given 1 Reactant
    if sum_reactants == 1:
        given = state.reactants[given_reactants[0]]
        state = calculate_initial_reactant(state, given)
        content.append("Reactants Required:\n")
        for reactant in state.reactants:
            if reactant.formula:
                content.append(reactant.formula + ": " + str(round(reactant.initial, 3)) + "g\n")
        state = calculate_final_product(state, given)
        content.append("\nProducts Produced:\n")
        for product in state.products:
            if product.formula:
                content.append(product.formula + ": " + str(round(product.final, 3)) + "g\n")
        content.append("\n")
        content.append(Button("Reset", "reset"))
        content.append(Button("Edit Inputs", "edit_input"))
        return Page(
            state,
            content
            )
    #Given 1+ Reactants
    if sum_reactants > 1:
        given = state.reactants[identify_limiting(state.reactants)]
        state = calculate_final_reactant(state, given)
        state = calculate_initial_reactant(state, given)
        content.append("Reactants Consumed:\n")
        for reactant in state.reactants:
            if reactant.formula:
                content.append(reactant.formula + ": " + str(round(reactant.initial, 3)))
                content.append("   " + "(Remaining: " + str(round(reactant.final, 3)) + "g)\n")
        state = calculate_final_product(state, given)
        content.append("\nProducts Produced:\n")
        for product in state.products:
            if product.formula:
                content.append(product.formula + ": " + str(round(product.final, 3)) + "g\n")
        content.append("\n")
        content.append(Button("Reset", "reset"))
        content.append(Button("Edit Inputs", "edit_input"))
        return Page(
            state,
            content
            )
    
    
@route
def reset(state: State) -> Page:
    """
    Return user to starting page, reset state dataclass.
    
    Arguemnts:
        state(State): the current state of the program
    Return:
        Page: the home page of the program
    """
    
    return index(State("", [], [], ""))


@route
def edit_input(state: State) -> Page:
    """
    Set all initials and final values to 0 and returns user to amount input page.
    
    Arguments:
        state(State): the current state of the program
    Return:
        Page: the input amount page
    """
    
    for i in range(len(state.reactants)):
        state.reactants[i].initial = 0.
        state.reactants[i].final = 0.
    for idnex in range(len(state.products)):
        state.products[i].initial = 0.
        state.products[i].final = 0.
    return confirm_formula(state)







start_server(State("", [], [], ""), project_packages=["molmass"])
