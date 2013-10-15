import diary_range
import sys
    
from presenter import display_entries

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        display_entries(diary_range.last(100))
    else:
        display_entries(diary_range.process_args())
