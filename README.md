# SPEC_perfmon_driver

SPEC_perfmon_driver is a Python script that runs SPECviewPerf2020 on the sw viewset and reports results including memory
and processor utilization obtained from perfmon.

## Requirements

- python (script is in python)
- SPECviewPerf2020 (program the script invokes)
- pandas (used to handle perfmon log data)
- numpy (used to clean log data)
- matplotlib (used to chart utilization data)
- xml.etree (used to process SPECviewPerf2020 results)
- reportlab (used to generate pdf report)

## Usage

clone the repo into your computer
``` bash
git clone [url]
```

open the directory and run the script
``` bash
cd [script directory]
python .\run.py
```

## Output
You should get a pdf report containing the composite score, the average composite score from the SPECviewPerf runs,
and the memory and process utilization data.

##Issues
SPECviewPerf uses unpredictable naming for the results folder which lead me to rely on getting the data from the latest
modified folder assuming it will be the one associated with the test just executed.

##Future Features
- Add support for user input to allow customization of (viewset, num_iterations, window size, what data perfmon logs, etc.)
- Add support for running the script in any filesystem setup (remove hardcoded directory paths and replace them with environment variables)
- Beautify the pdf report.

## License
[MIT](https://choosealicense.com/licenses/mit/)