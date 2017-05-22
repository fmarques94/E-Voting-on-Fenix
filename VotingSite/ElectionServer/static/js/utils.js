function IsCSV(Fileform){
    input = Fileform.elements["File"];
    console.log(input)
    if (input.type == "file") {
        filename = input.value;
        if(filename.length>0){
            console.log(filename.substr(filename.length - 4, 4).toLowerCase() == '.csv')
            return filename.substr(filename.length - 4, 4).toLowerCase() == '.csv';
        }
    }
    return false;
}