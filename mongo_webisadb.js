// (1) Download (and unzip) the MongoDB dump of the WebIsA Database from:
// http://webdatacommons.org/isadb/
// or more speficially: http://data.dws.informatik.uni-mannheim.de/webisadb/repo/tuples-webisadb-april-2016.tar.gz

// (2) Restore the dump using `mongorestore`.
// When the database crashes during that process, restart `mongod` and enter the following into the Mongo shell (`mongosh`):

db.getCollectionNames().map((collname) => "--excludeCollection=" + collname + " ").join(" ")

// ...and insert that string into your `mongorestore` command
// to prevent `mongorestore` from trying to restore the collections again that it already has!

// (3) Once the WebIsA Database is restored, create these indexes in the Mongo shell:

db.getCollectionNames().forEach(function(collectionName) { db[collectionName].createIndex({instance: 1}); console.log("Created Index for " + collectionName); });

// (4) Important: Increase the OS maximum file limit (in the regular shell):
// $ ulimit -n 1000000

// (5) Execute the following command in Mongo shell (replace "vader" with your instance search string):
let searchTerm = "vader";
let topK = 10;
let res = []; // sorted results
let collectionsDoneCounter = 0;
db.getCollectionNames().forEach(function(collectionName) {
    db[collectionName].find({instance: searchTerm}).forEach(function(item) {
        item.modifications.forEach(function(m) {
            let indexToInsert = 0;
            while (indexToInsert < res.length && res[indexToInsert][6] >= m.frequency) {indexToInsert++;}
            res.splice(indexToInsert, 0, [m.ipremod, item.instance, m.ipostmod, m.cpremod, item.class, m.cpostmod, m.frequency]);
        });
    });
    collectionsDoneCounter++;
    console.log("");
    console.log("After searching in " + collectionsDoneCounter + " collections:")
    for (let i = 0; i < Math.min(topK, res.length); i++) {
        console.log(res[i][0] + " | " + res[i][1] + " | " + res[i][2] + " | " + res[i][3] + " | " + res[i][4] + " | " + res[i][5] + " | " + res[i][6]);
    }
});

// (6) The "vader" example will return:
// [...]
//
// After searching in 1406 collections:
// darth | vader |  | star wars | character |  | 167
// darth | vader |  | star wars | character |  | 167
// darth | vader |  |  | character |  | 83
// darth | vader |  |  | character |  | 83
// darth | vader |  |  | villain |  | 43
// darth | vader |  |  | villain |  | 43
// darth | vader |  |  | none |  | 41
// darth | vader |  |  | none |  | 41
//  | vader |  |  | band |  | 34
//  | vader |  |  | band |  | 34

