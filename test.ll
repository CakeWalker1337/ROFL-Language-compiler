
%struct.a = type {i32}

define %struct.a @func.ss() {
    %c.ptr = alloca %struct.a
    %c.1 = load %struct.a, %struct.a* %c.ptr
    ret %struct.a %c.1
}

define i32 @main() {
    %ss.2 = call %struct.a @func.ss()
    %ss.3.ptr = alloca %struct.a
    %store a %ss.2, a* ss.3.ptr
    %struct.a.0.4.ptr = getelementptr inbounds %struct.a, %struct.a* %ss.3.ptr, i32 0, i32 0
    %struct.a.0.4.4 = load i32, i32* %struct.a.0.4.ptr
    %buffer7 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.1, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer7, i32 %struct.a.0.4.4)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
