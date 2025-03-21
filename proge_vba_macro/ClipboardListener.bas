Attribute VB_Name = "ClipboardListener"
Option Explicit

#If VBA7 Then
    Declare PtrSafe Function SetTimer Lib "user32" (ByVal hwnd As LongPtr, ByVal nIDEvent As LongPtr, ByVal uElapse As Long, ByVal lpTimerFunc As LongPtr) As LongPtr
    Declare PtrSafe Function KillTimer Lib "user32" (ByVal hwnd As LongPtr, ByVal nIDEvent As LongPtr) As Long
#Else
    Declare Function SetTimer Lib "user32" (ByVal hwnd As Long, ByVal nIDEvent As Long, ByVal uElapse As Long, ByVal lpTimerFunc As Long) As Long
    Declare Function KillTimer Lib "user32" (ByVal hwnd As Long, ByVal nIDEvent As Long) As Long
#End If

' Global variables
#If VBA7 Then
    Public timerID As LongPtr
#Else
    Public timerID As Long
#End If
Public lastClipboard As String

' Timer callback procedure
#If VBA7 Then
    Public Sub TimerProc(ByVal hwnd As LongPtr, ByVal uMsg As Long, ByVal nIDEvent As LongPtr, ByVal dwTime As Long)
#Else
    Public Sub TimerProc(ByVal hwnd As Long, ByVal uMsg As Long, ByVal nIDEvent As Long, ByVal dwTime As Long)
#End If
    On Error Resume Next
    Dim clipboardText As String
    Dim dataObj As Object
    
    ' Access clipboard using late binding
    Set dataObj = CreateObject("HTMLFile")
    clipboardText = dataObj.ParentWindow.ClipboardData.GetData("Text")
    
    ' Process clipboard only if it has changed
    If clipboardText <> lastClipboard Then
        lastClipboard = clipboardText
        Dim coords As Variant
        coords = ExtractCoordinates(clipboardText)
        
        ' If valid coordinates are found, create a point
        If Not IsEmpty(coords) Then
            CreatePoint coords(0), coords(1), coords(2)
        End If
    End If
End Sub

' Extract X, Y, Z coordinates from clipboard text
Public Function ExtractCoordinates(ByVal text As String) As Variant
    On Error Resume Next
    
    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    
    ' Replace newlines with spaces to handle multi-line formats
    text = Replace(Replace(text, vbCr, " "), vbLf, " ")
    
    ' Updated pattern to handle coordinates with spaces or that were on separate lines
    regex.Pattern = "Position:[\s\r\n]*(\d+\.\d+)[\s\r\n]+(\d+\.\d+)[\s\r\n]+(\d+\.\d+)m"
    regex.Global = False
    regex.IgnoreCase = True
    
    Dim matches As Object
    Set matches = regex.Execute(text)
    
    If matches.Count = 1 Then
        ExtractCoordinates = Array(matches(0).SubMatches(0), matches(0).SubMatches(1), matches(0).SubMatches(2))
        Debug.Print "Coordinates extracted: " & matches(0).SubMatches(0) & ", " & _
                    matches(0).SubMatches(1) & ", " & matches(0).SubMatches(2)
    Else
        ExtractCoordinates = Empty
        Debug.Print "No coordinates found in text: " & text
    End If
End Function
' Create a point based on clipboard coordinates
Public Sub CreatePoint(ByVal x As String, ByVal y As String, ByVal z As String)
    On Error Resume Next

    ' Get active IntelliCAD document
    Dim icadDoc As IntelliCAD.Document
    Set icadDoc = ActiveDocument

    ' Create point and add to model space
    Dim myPoint As IntelliCAD.Point
    Set myPoint = Library.CreatePoint(CDbl(x), CDbl(y), CDbl(z))

    Dim myPtEnt As IntelliCAD.PointEntity
    Set myPtEnt = icadDoc.ModelSpace.AddPointEntity(myPoint)

    ' Update the point entity
    myPtEnt.Update

End Sub


' Start the timer
Public Sub StartMonitoring()
    Debug.Print "Clipboard monitoring started"
    If timerID = 0 Then
        #If VBA7 Then
            timerID = SetTimer(0, 0, 50, AddressOf TimerProc) ' 50 ms interval
        #Else
            timerID = SetTimer(0, 0, 50, AddressOf TimerProc)
        #End If
        ' Initialize lastClipboard to avoid initial false positive
        On Error Resume Next
        Dim dataObj As Object
        Set dataObj = CreateObject("HTMLFile")
        lastClipboard = dataObj.ParentWindow.ClipboardData.GetData("Text")
    End If
End Sub

' Stop the timer
Public Sub StopMonitoring()
    If timerID <> 0 Then
        #If VBA7 Then
            KillTimer 0, timerID
        #Else
            KillTimer 0, timerID
        #End If
        timerID = 0
        Debug.Print "Clipboard monitoring stopped"
    End If
End Sub