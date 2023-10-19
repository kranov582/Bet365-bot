import sys
import io

old_stdout = sys.stdout # Memorize the default stdout stream
sys.stdout = buffer = io.StringIO()

print('47564654')

# Call your algorithm function.
# etc...

sys.stdout = old_stdout # Put the old stream back in place

whatWasPrinted = buffer.getvalue() # Return a str containing the entire contents of the buffer.
print(whatWasPrinted) # Why not to print it?