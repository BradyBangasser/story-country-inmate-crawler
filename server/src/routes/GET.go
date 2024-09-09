package routes

import (
    "github.com/gin-gonic/gin"
    "time"
)

func GET(c *gin.Context) {
    currentTime := time.Now()
    c.JSON(200, gin.H{"time": currentTime.String()})
}
