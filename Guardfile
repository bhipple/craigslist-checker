guard :shell do
    watch(%{.py$}) do
        system('clear')
        system('rm -f results.csv')
        system('python craigslist.py "bicycle 50cm" "benjamin.hipple@gmail.com"')
        system('cat results.csv')
    end
end
