package src

import (
    "errors"
    "time"
    "os"
    "encoding/json"
    "io"
)

// TODO Implement Database
// Probably SQLite


type DatabaseProvider struct {

}

type Charge struct {
    Law string `json:"law"`
    Bond float32 `json:"bond"`
    BondStatus int8 `json:"bondStatus"`
    Description string `json:"des"`
    Date string `json:"date"`
}

type Criminal struct {
    FirstName string `json:"first"`
    MiddleName string `json:"middle"`
    LastName string `json:"last"`
    Race string `json:"race"`
    Charges []Charge `json:"charges"`
}

type CriminalJson struct {
    Inmates []Criminal `json:"inmates"`
    CachedAt time.Time
}

var crimCache CriminalJson

func InitDatabase() (*DatabaseProvider, error) {
    return nil, errors.New("Not Implemented Yet")
}

func GetInmates() ([]Criminal, error) {
    now := time.Now()
    if now.Hour() != crimCache.CachedAt.Hour() {
        jsonFile, err := os.Open("roster.json")

        if err != nil {
            return nil, err
        }

        defer jsonFile.Close()

        jsonBytes, _ := io.ReadAll(jsonFile)

        err = json.Unmarshal(jsonBytes, &crimCache)

        if err != nil {
            return nil, err
        }
    }
    return crimCache.Inmates, nil
}
