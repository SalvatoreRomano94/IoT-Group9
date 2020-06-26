function initialize() {
	Z.init({
        on_event: event_callback,
        on_connected: connected_callback
        //on_offline: offline_callback
    });

    $(".myslider").hide();
    $(".form_orario").hide();
    $("#security").hide();
    $("#alarm_information").hide();
    $('#slide').change(slide_callback);
    $('#send_alarm').click(alarm_callback);
    $('#automatic').change(radio_callback);
    $('#manual').change(radio_callback);
    $("#alarm_but").click(alarm_but_callback);
    $('#cancel_alarm').click(cancel_alarm_callback);
    $('#stop_security').click(stop_security_callback);
}

var intervalId = 0;

function event_callback(event) {
    var modality=event.payload.modality;
    var state=event.payload.state;
    var alarm=event.payload.alarm;
    var security = event.payload.security;

    if(security){
        intervalId = setInterval("immagineLampeggiante()", 500);
        $("#security").show();
    }else{
        $('#security').hide();
        clearInterval(intervalId);
        $('#planimetria').attr("src", "planimetria-casa-block.jpg");
    }

    state_int = parseInt(state);
    if(state_int == -90){
        $('#state').text("open");
        $('#planimetria').attr("src", "planimetria-casa-open.jpg");
    }else if(state_int == 90){
        $('#state').text("close");
        $('#planimetria').attr("src", "planimetria-casa-block.jpg");
    }else{
        $('#state').text(state_int+90);
        $('#planimetria').attr("src", "planimetria-casa-automatic.jpg");
    }

    $('#slide').val(state_int);
    document.getElementById('val').innerHTML = state_int + 90;

    if(modality == "automatic"){
        document.getElementById('automatic').checked = true;
        document.getElementById('manual').checked = false;
        $(".myslider").hide();
    }else{
        document.getElementById('automatic').checked = false;
        document.getElementById('manual').checked = true;
        $(".myslider").show();
    }

    if(!alarm){
        $("#alarm_information").hide();
        document.getElementById('alarm_but').disabled = false; 
    }
    
    $('#modality').text(modality);
    //$('#state').text(state);
    $('#alarm').text(alarm? "Yes": "No");
}

function immagineLampeggiante(){
    if($('#planimetria').attr("src") == "planimetria-casa-block.jpg"){
        $('#planimetria').attr("src","planimetria-casa-alarm.jpg");
    }else{
        $('#planimetria').attr("src","planimetria-casa-block.jpg");
    }
}

function stop_security_callback(){
    Z.call('stop_security',[42],stop_security_callback_result);
}

function stop_security_callback_result(msg){
    var sec = msg.res;
    if(!sec){
        $('#security').hide();
        clearInterval(intervalId);
        $('#planimetria').attr("src", "planimetria-casa-block.jpg");
    }
}

function slide_callback() {
    var value=$('#slide').val();
    value=parseInt(value);
    Z.call('set_angle', [value], result_callback_slide);
}

function alarm_callback() {
    var hour = $('#hour').val();
    hour = parseInt(hour);
    var minute = $('#minute').val();
    minute = parseInt(minute);
    var data = new Date();
    current_hour = parseInt(data.getHours());
    current_minute = parseInt(data.getMinutes());
    if(current_hour - hour <= 0){
        diff_hour = -(current_hour - hour);
    }else{
        diff_hour = 24 - (current_hour - hour);
    }

    if(current_minute - minute >0 ){
        diff_hour -= 1;
        diff_minute = 60 - (current_minute - minute);
    }else{
        diff_minute = -(current_minute - minute);
    }
    delay = (diff_minute * 60 * 1000) + (diff_hour * 60 * 60 * 1000);
    $("#alarm_information").show();
    document.getElementById('alarm_clock').innerHTML = String(hour) + ':' + String(minute);
    document.getElementById('alarm_but').disabled = true; 
    $(".form_orario").hide();
    Z.call('set_alarm', [delay], result_alarm_callback);
}

function cancel_alarm_callback(){
    document.getElementById('alarm_but').disabled = false;
    $("#alarm_information").hide();
    Z.call('stop_alarm',[80],result_alarm_callback);
}

function result_alarm_callback(msg){
    var al = msg.res;
    $('#alarm').text(al? "Yes": "No")
}

function result_callback_slide(msg) {
    var angle=msg.res;
    $('#slide').val(angle);
}

function result_callback_mod(msg) {
    var mod=msg.res;
    $('#modality').text(mod);
    if(mod == "automatic"){
        document.getElementById('automatic').checked = true;
        document.getElementById('manual').checked = false;
        $(".myslider").hide();
    }
    if(mod == "manual"){
        document.getElementById('automatic').checked = false;
        document.getElementById('manual').checked = true;
        $(".myslider").show();
    }
}

function update(value,elem) {
    document.getElementById(elem).innerHTML = parseInt(value) + 90;
}

function connected_callback() {
    Z.call('init', [42], result_callback_connected);
}

function result_callback_connected(msg){
    var tup = msg.res;
    
    $('#modality').text(tup[0]);
    if(tup[0] == "automatic"){
        document.getElementById('automatic').checked = true;
        document.getElementById('manual').checked = false;
        $(".myslider").hide();
    }
    if(tup[0] == "manual"){
        document.getElementById('automatic').checked = false;
        document.getElementById('manual').checked = true;
        $(".myslider").show();
    }
    
    state_int = parseInt(tup[1]);
    $('#slide').val(state_int);
    if(state_int == -90){
        $('#state').text("open");
        $('#planimetria').attr("src", "planimetria-casa-open.jpg");
    }else if(state_int == 90){
        $('#state').text("close");
        $('#planimetria').attr("src", "planimetria-casa-block.jpg");
    }else{
        $('#state').text(state_int+90);
        $('#planimetria').attr("src", "planimetria-casa-automatic.jpg");
    }
    
    $('#alarm').text(tup[2]? "Yes": "No");

    if(tup[3]){
        intervalId = setInterval("immagineLampeggiante()", 500);
        $("#security").show();
    }else{
        $('#security').hide();
        clearInterval(intervalId);
        $('#planimetria').attr("src", "planimetria-casa-block.jpg");
    }
}

function radio_callback(){
    var mod = document.querySelector('input[name = "function"]:checked').value;

    if(mod == "automatic"){
        $(".myslider").hide();
        Z.call('set_mod',["automatic"],result_callback_mod);
    }
    if(mod == "manual"){
        $(".myslider").show();
        Z.call('set_mod',["manual"],result_callback_mod);
    }
}

function alarm_but_callback(){
    $(".form_orario").toggle();
}




