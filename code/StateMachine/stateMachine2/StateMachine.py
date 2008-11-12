# StateMachine/stateMachine2/StateMachine.py
# A table-driven state machine

class StateMachine:
    def __init__(self, initialState, tranTable):
        self.state = initialState
        self.transitionTable = tranTable

    def nextState(self, input):

        Iterator it=((List)map.get(state)).iterator()
        while(it.hasNext()):
            Object[] tran = (Object[])it.next()
            if(input == tran[0] ||
               input.getClass() == tran[0]):
                if(tran[1] != null):
                    Condition c = (Condition)tran[1]
                    if(!c.condition(input))
                        continue # Failed test

                if(tran[2] != null)
                    ((Transition)tran[2]).transition(input)
                state = (State)tran[3]
                return


        throw RuntimeException(
          "Input not supported for current state")