const api_url = 'http://localhost:8086'
 mocha.setup('bdd');
 let randnum2 = (Math.floor(Math.random() * 10203040))
 auth_name2 = 'player_test'+ randnum2
 auth_pass2 = '12345'
 let randnum = (Math.floor(Math.random() * 10203040))
 auth_name = 'user_test'+ randnum
 auth_pass = '12345'
 let randnum3 = (Math.floor(Math.random() * 10203040))
 auth_name3 = 'player_test'+ randnum3
 auth_pass3 = '12345'
 let randnum4 = (Math.floor(Math.random() * 10203040))
 auth_name4 = 'player_test'+ randnum4
 auth_pass4 = '12345'
 let randnum5 = (Math.floor(Math.random() * 10203040))
 auth_name5 = 'player_test'+ randnum5
 auth_pass5 = '12345'
 let randnum6 = (Math.floor(Math.random() * 10203040))
 auth_name6 = 'player_test'+ randnum6
 auth_pass6 = '12345'
 let randnum7 = (Math.floor(Math.random() * 10203040))
 auth_name7 = 'player_test'+ randnum7
 auth_pass7 = '12345'
 let randnum8 = (Math.floor(Math.random() * 10203040))
 auth_name8 = 'player_test'+ randnum8
 auth_pass8 = '12345'
 auth_name9 = 'player_test'+ randnum8
 auth_pass9 = '12345'

 function getfromserver(url, data, headers=null){
    return $.ajax({
        url: url,
        headers: headers,
        type:  'POST',
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function getrequesttoserver(url, data, headers=null){
    return $.ajax({
        url: url,
        headers: headers,
        type:  'GET',
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function deleterequesttoserver(url, data, headers=null){
    return $.ajax({
        url: url,
        headers: headers,
        type:  'DELETE',
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

describe('general tests', () => {
    it('test player registration', async () => {
        let x = await getfromserver(api_url + '/register',{
            email: auth_name,
            passwordHash: auth_pass,
            role: "player"
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
    }).timeout(3500)

    it('registered player can authenticate multiple times', async()=>{
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name,
            passwordHash: auth_pass
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
    })


    it('test instructor registration', async() =>{
        let x = await getfromserver(api_url + '/register',{
            email: auth_name2,
            passwordHash: auth_pass2,
            role: "instructor"
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
    })

    it('registered instructor can authenticate multiple times', async()=>{
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
    })

    it('instructor can get demand patterns from server', async()=>{
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        let req = await $.ajax({
            url: api_url+'/instructor/demand_patterns',
            headers: {'SESSION-KEY': x['SESSION-KEY']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        chai.assert(req.length > 0)
    })

    const demand_pattern = {
        "name": "testing",
        "encoded_data": "1,2,3,4",
    }

    it('instructor can add demand patterns to demand pattern table', async()=>{
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        let added_demand = await getfromserver(api_url + '/instructor/add_demand_patterns', demand_pattern, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(added_demand)
        chai.expect(added_demand['demand_pattern']).not.equal(null)
    })
});

describe('game tests', () => {
    // an array to keep track of all games we've created 
    games = []
    it('instructor can create game', async()=>{
        // try to be atomic in our testing
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        console.log(x)
        let game_creation = await getfromserver(api_url + '/instructor/game', {
        }, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        games.push(game_creation['game_id'])
    })

    it('non-authenticated user cannot create game', async()=>{
        // this should surely fail since we do not include the header
        try{
            let game_creation = await getfromserver(api_url + '/instructor/game', {
            })
            console.log(game_creation)
            chai.expect(1).to.eql(2).withErrorMessage("expected an error to be thrown");
        }
        catch(err){
            return
        } 
    })
    const params = {
        "session_length": 21,
        "retailer_present": true,
        "wholesaler_present": false,
        "holding_cost": 6.9,
        "backlog_cost": 4.20,
        "active": true,
        "starting_inventory": 5,
        "info_delay": 22,
        "info_sharing": true,
    }
    it('instructor can create game with custom parameters', async()=>{
        // try to be atomic in our testing
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        console.log(x)

        let game_creation = await getfromserver(api_url + '/instructor/game', params, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        games.push(game_creation['game_id'])
        //now get all the game parameters
    })
    it('instructor can modify game with custom parameters', async()=>{
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        console.log(x)

        let game_creation = await getfromserver(api_url + '/instructor/game', {}, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        games.push(game_creation['game_id'])
        let modify = await $.ajax({
            url: api_url+'/instructor/modify_game/'+game_creation['game_id'],
            headers: {'SESSION-KEY': x['SESSION-KEY']},
            type:  'PUT',
            data: JSON.stringify(params),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        console.log(modify);

        for (var k in params){
            // EXPLICITLY USE == BECAUSE OF TYPE MISMATCHES
            console.log(`comparing: (${params[k]}, ${modify[k]})`)
            chai.assert(params[k] == modify[k])
            
        }
    })
    it('instructor can get game info, game info is correct', async()=>{
        // try to be atomic in our testing
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        // create another game just to be sure
        let game_creation = await getfromserver(api_url + '/instructor/game', params, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        r = await $.ajax({
            url: api_url+'/instructor/game/'+game_creation['game_id'],
            headers: {'SESSION-KEY': x['SESSION-KEY']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        for (var k in params){
            // EXPLICITLY USE == BECAUSE OF TYPE MISMATCHES
            console.log(`comparing: (${params[k]}, ${r[k]})`)
            chai.assert(params[k] == r[k])
            
        }
               //now get all the game parameters
    }) 
    it('instructor can get all games he created', async()=>{
        // try to be atomic in our testing
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        // create another game just to be sure
        let game_creation = await getfromserver(api_url + '/instructor/game', params, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        games.push(game_creation['game_id']);
        r = await $.ajax({
            url: api_url+'/instructor/game',
            headers: {'SESSION-KEY': x['SESSION-KEY']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        console.log(r)
               //now get all the game parameters
    })

    it("instructor who created no games receives empty response", async()=>{
        let x = await getfromserver(api_url + '/register',{
            email: auth_name3,
            passwordHash: auth_pass3,
            role: "instructor"
        })

        chai.expect(x['SESSION-KEY']).not.equal(null)

        r = await $.ajax({
            url: api_url+'/instructor/game',
            headers: {'SESSION-KEY': x['SESSION-KEY']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        console.log(r);
        chai.expect(r).to.be.empty;

    })

    it("instructor can get the player table", async()=>{
        let x = await getfromserver(api_url + '/register',{
            email: auth_name8,
            passwordHash: auth_pass8,
            role: "instructor"
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        let actual_test = await getrequesttoserver(
            api_url + '/instructor/get_players_table',
            {},
            {"SESSION-KEY": x['SESSION-KEY']}
        )

        chai.assert(actual_test.length > 0);

    }).timeout(3000)

    it("instructor can add players to the game specified", async()=>{
        let y = await getfromserver(api_url + '/register',{
            email: auth_name4,
            passwordHash: auth_pass4,
            role: "player"
        })
        chai.expect(y['SESSION-KEY']).not.equal(null)
        console.log(y['id'])
        let z = await getfromserver(api_url + '/register',{
            email: auth_name5,
            passwordHash: auth_pass5,
            role: "player"
        })
        chai.expect(z['SESSION-KEY']).not.equal(null)

        let x = await getfromserver(api_url + '/register', {
            email: auth_name9,
            passwordHash: auth_pass9,
            role: "instructor"
        })
        let game_creation = await getfromserver(api_url + '/instructor/game', {},
         {"SESSION-KEY": x['SESSION-KEY']})

        chai.expect(game_creation['game_id']).not.equal(null)
        games.push(game_creation['game_id'])

        chai.expect(x['SESSION-KEY']).not.equal(null)
        let actual_test = await getfromserver(
            api_url + '/instructor/add_player_to_game',
            {"factory_id": y['id'], "distributor_id": z['id'], "wholesaler_id": 0, "retailer_id": 0, "game_id": game_creation['game_id']},
            {"SESSION-KEY": x['SESSION-KEY']}
        )
        console.log(actual_test)
        chai.assert(actual_test['success_factory'] === true)
        chai.assert(actual_test['success_distributor'] === true)

        let test = await getrequesttoserver(
            api_url + '/instructor/get_players_table',
            {},
            {"SESSION-KEY": x['SESSION-KEY']}
        )
        console.log(test[0])
        console.log(x[0])
        for(i=0; i<test.length; i++)
        {
            if(test[i].current_game_id === game_creation['game_id'] && test[i].role === "distributor"){
                chai.assert(test[i].id === z['id'])
            }
        } 

    }).timeout(3000)

    it("instructor can get players not playing", async()=>{
        let y = await getfromserver(api_url + '/register',{
            email: auth_name7,
            passwordHash: auth_pass7,
            role: "instructor"
        })
        chai.expect(y['SESSION-KEY']).not.equal(null)
        let x = await getrequesttoserver(api_url + '/instructor/get_players_not_playing',{}, {'SESSION-KEY': y['SESSION-KEY'] })
        a = x.length 
        for(i=0; i<a; i++)
        {
            if(x[i].email === auth_name4)
                chai.expect(x[i].email).to.equal(auth_name4);
        }
    }).timeout(3000)

    it('player cannot join more than one game', async() =>{
        x = await getfromserver(api_url + '/authenticate',{
            email: auth_name,
            passwordHash: auth_pass,
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        try{
            let actual_test = await getfromserver(
                api_url + '/game/join/'+ games[0],
                {role: 'distributor'},
                {"SESSION-KEY": x['SESSION-KEY']}
            )
            chai.fail()
        }
        catch(err){
            console.log(err)
        }
        //try to join another game using a different role
        try{
            let actual_test = await getfromserver(
                api_url + '/game/join/'+ games[0],
                {role: 'factory'},
                {"SESSION-KEY": x['SESSION-KEY']}
            )
            chai.fail()
        }
        catch(err){
            console.log(err);
        }
    })
    it("player can get information about his game only if he's authenticated", async() =>{
        try{
                let actual_test = await getrequesttoserver(
                    api_url + '/player/current_game',
                    {},
                )
                //fail if non-authenticated user tries to send the request
                assert.fail
            }
            catch (e){
                console.log(e)
            }
        
        x = await getfromserver(api_url + '/authenticate',{
            email: auth_name4,
            passwordHash: auth_pass4,
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)

        let actual_test = await getrequesttoserver(
            api_url + '/player/current_game',
            {},
            {"SESSION-KEY": x['SESSION-KEY']}
        )
        console.log(actual_test)
    });

    

    it("player can get information about a game if provided the game id, game info is correct", async()=>{
        // try to be atomic in our testing
        let x = await getfromserver(api_url + '/authenticate', {
            email: auth_name2,
            passwordHash: auth_pass2
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        // create another game just to be sure
        let game_creation = await getfromserver(api_url + '/instructor/game', params, {'SESSION-KEY': x['SESSION-KEY']})
        console.log(game_creation)
        chai.expect(game_creation['game_id']).not.equal(null)
        let y = await getfromserver(api_url + '/authenticate', {
            email: auth_name4,
            passwordHash: auth_pass4
        })
        chai.expect(x['SESSION-KEY']).not.equal(null)
        r = await $.ajax({
            url: api_url+'/player/game/'+game_creation['game_id'],
            headers: {'SESSION-KEY': y['SESSION-KEY']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
        for (var k in params){
            // EXPLICITLY USE == BECAUSE OF TYPE MISMATCHES
            console.log(`comparing: (${params[k]}, ${r[k]})`)
            chai.assert(params[k] == r[k])
            
        }
               //now get all the game parameters
    }) 



});
describe('simulate playing a game with 4 players and 1 instructor', async() => {
    let game = {};
    function randuser(){ return 'user'+ Math.floor(Math.random() * 10203099220); }
    const roles = ['distributor', 'retailer' , 'wholesaler', 'factory']
    it ('setting up game without errors', async(done)=>{
    
        let pass = '1234'
        
        let ins = await getfromserver(api_url + '/register',{
            email: randuser(),
            passwordHash: pass,
            role: "instructor"
        })
        let game_creation = await getfromserver(api_url + '/instructor/game', {
        }, {'SESSION-KEY': ins['SESSION-KEY'] })


        game['instructor'] = ins['SESSION-KEY'];
        for (const role of roles){
            let p = await getfromserver(api_url + '/register',{
                email: randuser(),
                passwordHash: pass,
                role: "player"
            })
            game[role] = p['SESSION-KEY']
        }
        for (const role of roles){
            let in_game = await getfromserver(
                api_url + '/game/join/'+ game_creation['game_id'],
                {role: role},
                {"SESSION-KEY": game[role]}
            );

        }

        ['distributor', 'retailer' , 'wholesaler', 'factory'].forEach( (i) =>{
            chai.assert(i in game);
        })
    }).timeout(30000)

    it ('playing a round, round is played after everyone orders', async()=>{
        this.setTimeout(5000);
        for (role of roles){
            console.log(game[role])
            let order = await getfromserver(
                api_url + '/game/round',
                {order: 5},
                {"SESSION-KEY": game[role]}
            )
            console.log(role)
            console.log(order)

        }
        res = await $.ajax({
            url:api_url + '/game/round',
            headers: {"SESSION-KEY": game['distributor']},
            type:  'GET',
            contentType: 'application/json; charset=utf-8',
        });
        console.log(res)
        res = JSON.parse(res)
        // 2 weeks should be returned now that everyone ordered
        chai.expect(res.length).to.equal(2);
    }).timeout(5000)









});

