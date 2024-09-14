"""
Module providing functions for debug printouts.
"""

__author__ = "https://github.com/ImproperDecoherence"


import inspect

_debug_on = False
"""Flag indicating if debug printing is active."""

_debug_filter = set()
"""The current debug filter."""


def debugIsOn() -> bool:
    """Tests if debug printing is active."""
    global _debug_on
    return _debug_on


def debugFilter() -> list[str]:
    """Returns the current debug filter."""
    global _debug_filter
    return _debug_filter


def debugOn(on: bool, filter: list[str]) -> None:
    """Turns on and off the debug print outs and sets the debud filter.
    
    Args:
        on: True to set the debug prints on, False to set all debug printr off.
        filter: A list of names of modules and names of functions/methods.
          Debug prints which is in the context any of these modules or functions/methods
          will be printed (if 'on' is True), other debug prints will not be printed.
    """
    global _debug_on
    global _debug_filter

    old = _debug_on

    _debug_on = on
    _debug_filter = set(filter)

    if old != _debug_on:
        if _debug_on:
            print(f"Debug: ON | Filter: {_debug_filter}")
        else:
            print("Debug: OFF")



class _CallerAnalysis:
    """An instance of this class investigates the context in which is was created."""

    def __init__(self):
        caller_frame = inspect.stack()[2]

        self.caller_locals = caller_frame[0].f_locals
        self.caller_instance = self.caller_locals.get('self')
        self.caller_module_name = inspect.getmodule(caller_frame[0]).__name__
        self.caller_function_name =  inspect.currentframe().f_back.f_back.f_code.co_name


    def callerVariables(self) -> dict:        
        """Returns a dicionary dict[variable name, variable value] for local variables and class attributes."""

        caller_variables = {name: value for name, value in self.caller_locals.items()}        

        if self.caller_instance:
            caller_class_attributes = {name: value for name, value in self.caller_instance.__class__.__dict__.items()}
            caller_variables.update(caller_class_attributes)

        return caller_variables
    

    def callerModuleName(self) -> str:
        """Returns the name of the module in which context this class instance  was created."""
        return self.caller_module_name


    def callerClassName(self) -> str:
        """Returns the name of the class in which context this class instance was created."""

        if self.caller_instance:
            caller_class = self.caller_instance.__class__
            return caller_class.__name__
        else:
            return ""


    def callerFunctionName(self) -> str:
        """Returns the name of the function in which context this class instance was created."""
        return self.caller_function_name
    

    def context(self) -> set[str]:
        """Returns a set of class names, module names and fucnction/method names in which this class instance was created."""
        class_name = self.callerClassName()
        context = {self.callerModuleName(), self.callerFunctionName()}

        if len(class_name) > 0:
            context.update([class_name])
        return context


    def contextStr(self) -> str:
        """Returns a string which represents the context in which this class instance was created.
        
        The sting has the following format: '<module name>[.<class name>].<method/function name>'
        """
        class_str = self.callerClassName()
        module_str = self.callerModuleName() + " | "

        if len(class_str) > 0:
            class_str = class_str + "."
            module_str = ""

        return f"{module_str}{class_str}{self.callerFunctionName()}"


    def variableValue(self, variable_name: str):
        """Returns the value of the local variables with the name 'variable_name'."""
        return self.callerVariables()[variable_name]


    def matchFilter(self, filter: list[str]) -> bool:
        """Tests if any of the strings in 'filter' matches the module name, the class name
        or the function/method name in wich context this class instance was created.
        """
        return any(self.context() & filter)


    def __str__(self):
        """Enables printing of instances of this class."""
        return [self.context(), self.callerVariables().keys()].__str__()



def debugPrint(to_print: str, condition: bool = True):
    """Prints a the 'to_print' string if the 'condition' is True.
    
    Additional conditions for printing is defined by 'debugOn'.
    """

    if debugIsOn() and condition:
        caller_analysis = _CallerAnalysis()
        if caller_analysis.matchFilter(debugFilter()):
            print(caller_analysis.contextStr() + " : " + to_print)


def debugVariable(variable_name: str, condition: bool = True):
    """Prints a the 'variable_name' and its value if the 'condition' is True.
    
    Additional conditions for printing is defined by 'debugOn'.
    """
    
    if debugIsOn() and condition:
        caller_analysis = _CallerAnalysis()
        if caller_analysis.matchFilter(debugFilter()):
            print(caller_analysis.contextStr() + " : " + variable_name + " = " + str(caller_analysis.variableValue(variable_name)))
            
        
