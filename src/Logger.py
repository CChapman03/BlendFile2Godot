import os

class Logger:

    def __init__(self, func):
        self.log_file = None
        self.func = func
        self.debug = True
        if self.debug:
            self.log_file = open("../logs/Combine_Blend_Files.log", 'w')
            self.log_file.write("Combine_Blend_Files Debug: \n")
            self.log_file.write("==============================================\n\n")
            self.log_file.close()

    def __call__(self, *args, **kwargs):
        if self.debug:
            self.log_file = open("../logs/Combine_Blend_Files.log", 'a')
            self.log_file.write("----------------------------------------------\n")
            self.log_file.write("%s : %s\n" % ("Got To Function", self.func.__name__))
            self.log_file.write("----------------------------------------------\n")
            
            self.log_file.write("Args: \n")
            i = 0
            for a in args:
                arg_name = self.func.__code__.co_varnames[i]
                self.log_file.write("\t%s : %s\n" % (arg_name, a))
                i += 1
            
            res = None
            errors = False

            try:
                res = self.func(*args, **kwargs)
                self.log_file.write("\n\nReturn Value : %s" % str(res))
                errors = False
                self.log_file.write("\n%s : %s" % ("Errors", str(errors)))
            except:
                errors = True
                self.log_file.write("\n\n%s : %s" % ("Errors", str(errors)))

            self.log_file.write("\n\n----------------------------------------------\n\n")
            self.log_file.close()