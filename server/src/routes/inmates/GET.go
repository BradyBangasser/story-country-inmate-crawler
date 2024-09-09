package inmates

import (
    "github.com/gin-gonic/gin"
    "iastate-crim/src"
)

func GET(c *gin.Context) {
    inmates, err := src.GetInmates()

    if err != nil {
        c.JSON(500, gin.H { "error": err.Error() })
    } else {
        c.JSON(200, inmates) 
    }
}
